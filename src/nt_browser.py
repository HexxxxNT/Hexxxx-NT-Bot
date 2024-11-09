import string
from dataclasses import dataclass
from pathlib import Path
from random import uniform, randint, choice, choices
from time import sleep
from typing import Any, Final

import chromedriver_autoinstaller
from selenium.common import NoSuchElementException, TimeoutException

from undetected_chromedriver import Chrome, ChromeOptions

from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from win32api import GetKeyboardLayout


class LoginError(Exception):
    pass


@dataclass
class NtCredentials:
    username: str
    password: str


class NtBrowser:
    US_KEYBOARD_LAYOUT: Final[int] = 67699721

    NtUrl: Path = Path("https://www.nitrotype.com")
    NtRaceUrl: Path = NtUrl / "race"
    NtLoginUrl: Path = NtUrl / "login"

    def __init__(self) -> None:
        chromedriver_autoinstaller.install()
        self._driver: Chrome | None = None
        self._default_wait: WebDriverWait | None = None
        self._short_wait: WebDriverWait | None = None
        self._racing: bool = False


    def __enter__(self) -> "NtBrowser":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.quit()

    @property
    def racing(self) -> bool:
        return self._racing

    @property
    def size(self) -> tuple[int, ...]:  # PyCharm raises warning when using hint like "tuple[int, int]". Bug or correct?
        return tuple(self._driver.get_window_size().values()) if self._driver else (0, 0)

    @size.setter
    def size(self, size: tuple[int, ...]) -> None:
        if self._driver:
            self._driver.set_window_size(size[0], size[1])

    @property
    def position(self) -> tuple[int, ...]:
        return tuple(self._driver.get_window_position().values()) if self._driver else (0, 0)

    @position.setter
    def position(self, position: tuple[int, ...]) -> None:
        if self._driver:
            self._driver.set_window_position(position[0], position[1])


    def start(self) -> None:
        # chromedriver only supports qwerty (US): https://developer.chrome.com/docs/chromedriver/help/keyboard-support
        if GetKeyboardLayout() != NtBrowser.US_KEYBOARD_LAYOUT:
            raise OSError("Must install and use US (QWERTY) keyboard layout.")

        options: ChromeOptions = ChromeOptions()
        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
        )

        self._driver: Chrome = Chrome(options=options)
        self._default_wait: WebDriverWait = WebDriverWait(self._driver, 20)
        self._short_wait: WebDriverWait = WebDriverWait(self._driver, 3)

    def quit(self) -> None:
        try:
            if self._driver:
                self._driver.quit()
        except OSError:
            # Consume errors related to Chrome window handle. (Caused by undetected chromedriver???)
            pass

    def create_account(self) -> NtCredentials:
        self.race(100)  # <- pass first race as "human verification"
        self._default_wait.until(
            EC.presence_of_element_located(
                (By.ID, "username")
            )
        )

        get_random_str: callable = lambda length: "".join(choices(string.ascii_letters + string.digits, k=length))
        credentials: NtCredentials = NtCredentials(
            username=get_random_str(15),
            password=get_random_str(15)
        )

        self._driver.find_element(By.ID, "username").send_keys(credentials.username)
        self._driver.find_element(By.ID, "password").send_keys(credentials.password, Keys.ENTER)

        # Does not work for some reason. (Missing auto generated headers?) Might fix later...
        """get_random_str: callable = lambda length: "".join(choices(string.ascii_letters + string.digits, k=length))
                credentials: NtCredentials = NtCredentials(
                    username=get_random_str(15),
                    password=get_random_str(15)
                )

                response: Response = post(
                    url="https://www.nitrotype.com/api/v2/auth/register/username",
                    headers={
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "de-DE,en-US;q=0.7,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Referer": "https://www.nitrotype.com/race",
                        "Content-Type": "application/json",
                        "Origin": "https://www.nitrotype.com",
                        "DNT": "1",
                        "Sec-GPC": "1",
                        "Alt-Used": "www.nitrotype.com",
                        "Connection": "keep-alive",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin"
                    },
                    json={
                        "username": credentials.username,
                        "password": credentials.password,
                        "captchaToken": None,
                        "acceptPolicy": "on",
                        "receiveContact": "",
                        "tz": "Europe/Berlin",
                        "qualifying": 1,
                        "avgSpeed": 100,
                        "avgAcc": 95,
                        "carID": 9,
                        "raceSounds": "only_fx"
                    }
                )"""

        return credentials



    def login(self, username: str, password: str) -> None:
        self._driver.get(str(NtBrowser.NtLoginUrl))
        self._default_wait.until(
            EC.presence_of_element_located(
                (By.ID, "username")
            )
        )
        self._driver.find_element(By.ID, "username").send_keys(username)
        self._driver.find_element(By.ID, "password").send_keys(password, Keys.ENTER)

        try:
            self._short_wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "nav-link")
                )
            )
        except TimeoutException:
            self._driver.close()
            raise LoginError("Cannot log in.")

    def _add_mistakes(self, text: str, accuracy: float) -> str:
        """
        Add mistakes / wrong characters to a text. Slightly randomized.
        :param text: The text.
        :param accuracy: float like 98.8 or 64.12 or .2
        :return: the text
        """
        if accuracy != 100:
            error_count: int = int(len(text) / 100 * (100 - accuracy)) + randint(0, 3)
            error_positions: list[int] = [randint(0, len(text)) for _ in range(error_count)]

            for position in error_positions:
                random_char: str = choice(string.ascii_letters)
                text = text[:position] + random_char + text[position:]

        return text


    def race(self, wpm: float, accuracy: float | None = None) -> None:
        self._racing = True

        if not accuracy:
            accuracy = randint(95, 98)

        self._driver.get(str(NtBrowser.NtRaceUrl))

        cpm: float = (wpm * 5)
        cps: float = cpm / 60
        sleep_per_char: float = (1 / cps) * 0.69  # magic number, since delays are still a mystery and need to be compensated for


        race_loaded: bool = False
        while not race_loaded:
            # Wait for race loader:
            try:
                self._short_wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "raceLoader")
                    )
                )
                race_loaded = True
            except TimeoutException:
                pass

            if not race_loaded:
                # Might already be in another race:
                try:
                    modal_container: WebElement = self._driver.find_element(By.CLASS_NAME, "modal-container")
                    try_again_btn: WebElement = modal_container.find_element(By.XPATH, "/div/div/div/div[2]/button")
                    try_again_btn.click()
                except NoSuchElementException:
                    pass

            # Missed the race loader? Try with dash-letter:
            try:
                self._short_wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "dash-letter")
                    )
                )
                race_loaded = True
            except TimeoutException:
                pass


        try:
            # Wait for race to load fully:
            self._default_wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "dash-letter")
                )
            )
        except TimeoutException:
            # Something went terribly wrong! Try again!
            print("Something went wrong. Restarting race.")
            self.race(wpm, accuracy)
            return


        # Cookie / ads consent:
        try:
            self._driver.find_element(By.CLASS_NAME, "fc-cta-consent").click()
        except NoSuchElementException:
            pass

        sleep(3)

        try:
            while True:
                letters: list[WebElement] = self._driver.find_elements(By.CLASS_NAME, "dash-letter")
                typed_letters: list[WebElement] = self._driver.find_elements(By.CLASS_NAME, "is-correct")
                text: str = "".join([letter.text for letter in letters if letter not in typed_letters])

                text = self._add_mistakes(text, accuracy)

                chain: ActionChains = ActionChains(driver=self._driver)
                for char in text:
                    random_factor: float = uniform(.3, 1.8)
                    chain.send_keys(char)
                    chain.pause(sleep_per_char * random_factor)
                chain.perform()

                # raise exception if finished / no more waiting chars:
                self._driver.find_element(By.CLASS_NAME, "is-waiting")
        except NoSuchElementException:
            print("finished race")
            sleep(3)

        self._racing = False

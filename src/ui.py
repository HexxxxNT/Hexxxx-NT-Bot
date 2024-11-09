from threading import Thread
from time import sleep
from tkinter import Tk, Misc, Event, HORIZONTAL, messagebox
from tkinter.ttk import Entry, Label, Frame, Button, Scale

from PIL import Image
from PIL.Image import Resampling
from PIL.ImageTk import PhotoImage
from ttkthemes.themed_tk import ThemedTk

from src.nt_browser import NtBrowser, LoginError
from src.resources import APP_ICON, ANDROID
from src.texts import APP_NAME


class LoginFrame(Frame):
    def __init__(self, parent: Misc, nt_browser: NtBrowser) -> None:
        super().__init__(parent)
        self._nt_browser: NtBrowser = nt_browser
        self._subscribers: list[callable] = []

        logo_image_raw: Image = Image.open(ANDROID)
        image_height: int = 75
        image_size: tuple[int, int] = (
            int((image_height / logo_image_raw.size[1]) * logo_image_raw.size[0]),
            image_height
        )
        logo_image_raw = logo_image_raw.resize(image_size, Resampling.LANCZOS)
        logo_image: PhotoImage = PhotoImage(logo_image_raw)
        logo: Label = Label(self, image=logo_image)
        logo.image = logo_image
        logo.grid(row=0, column=0, columnspan=2, sticky="n")

        title_label: Label = Label(self, text=APP_NAME, font=("Arial", 30), justify="center", anchor="center")
        title_label.grid(row=1, column=0, columnspan=2, pady=(0, 30), sticky="new")

        usr_name_label: Label = Label(self, text="username: ")
        usr_name_label.grid(row=2, column=0, pady=5, sticky="w")

        self._usr_name_entry: Entry = Entry(self)
        self._usr_name_entry.grid(row=2, column=1, sticky="ew")

        usr_pwd_label: Label = Label(self, text="password: ")
        usr_pwd_label.grid(row=3, column=0, pady=5, sticky="w")

        self._usr_pwd_entry: Entry = Entry(self, show="*")
        self._usr_pwd_entry.grid(row=3, column=1, sticky="ew")

        login_button: Button = Button(self, text="login")
        login_button.grid(row=4, column=0, pady=5, columnspan=2, sticky="news")
        login_button.bind("<Button-1>", self._login_clicked)

        for row in range(self.grid_size()[1]):
            self.grid_rowconfigure(row, weight=0, minsize=1)

        self.grid_columnconfigure(0, weight=0, minsize=1)
        self.grid_columnconfigure(1, weight=1, minsize=1)

    def subscribe_to_login(self, some_callable: callable) -> None:
        self._subscribers.append(some_callable)

    def _notify_subscribers(self) -> None:
        for sub in self._subscribers:
            sub()

    def _login_clicked(self, event: Event) -> None:
        try:
            self._nt_browser.start()
            self._nt_browser.size = (500, 300)
            self._nt_browser.position = (
                self.master.winfo_rootx() - self._nt_browser.size[0],
                self.master.winfo_rooty()
            )

            self._nt_browser.login(
                self._usr_name_entry.get(),
                self._usr_pwd_entry.get()
            )
            self._notify_subscribers()
        except OSError:
            messagebox.showerror(
                "Couldn't detect US layout!",
                (
                    "This tool is only compatible with a US keyboard layout.\n\n"
                    "Install and activate a US (QWERTY) layout on your system and try again."
                )
            )
        except LoginError:
            messagebox.showerror(
                "Cannot log in.",
                (
                    f"Cannot log into the account \"{self._usr_name_entry.get()}\".\n"
                    "Please make sure that you have entered the correct credentials."
                )
            )


class RaceFrame(Frame):
    StartRacingText: str = "Start"
    StopRacingText: str = "Stop"
    WpmText: str = "Speed: {} WPM"
    AccText: str = "Accuracy: {} %"

    def __init__(self, parent: Misc, nt_browser: NtBrowser) -> None:
        super().__init__(parent)
        self._nt_browser: NtBrowser = nt_browser
        self._race_loop_running: bool = False

        wpm_bounds: tuple[int, int] = (1, 250)
        wpm_default: int = int(wpm_bounds[1] / 2)

        acc_bounds: tuple[int, int] = (1, 100)
        acc_default: int = acc_bounds[1] - 3

        disclaimer_label: Label = Label(
            self,
            text="Attention:\n"
                 "Please keep the settings moderate, unless you want to get banned.\n"
                 "The maximum wpm have been capped by design, to prevent your account from getting banned.\n"
                 "To evade detection, all of the values you set will be slightly randomized for each race.\n"
                 "You are using this software at your own risk! Your account may get banned!"
        )
        disclaimer_label.grid(row=0, column=0, pady=10, sticky="news")

        wpm_label: Label = Label(self, text=RaceFrame.WpmText.format(wpm_default))
        wpm_label.grid(row=1, column=0, sticky="nws")

        self._wpm_scale: Scale = Scale(self, from_=wpm_bounds[0], to=wpm_bounds[1], orient=HORIZONTAL)
        self._wpm_scale.set(wpm_default)
        self._wpm_scale.config(command=lambda v: wpm_label.config(text=RaceFrame.WpmText.format(int(float(v)))))
        self._wpm_scale.grid(row=2, column=0, sticky="news")

        acc_label: Label = Label(self, text=RaceFrame.AccText.format(acc_default))
        acc_label.grid(row=3, column=0, sticky="nws")

        self._accuracy_scale: Scale = Scale(self, from_=acc_bounds[0], to=acc_bounds[1], orient=HORIZONTAL)
        self._accuracy_scale.set(acc_default)
        self._accuracy_scale.config(command=lambda v: acc_label.config(text=RaceFrame.AccText.format(int(float(v)))))
        self._accuracy_scale.grid(row=4, column=0, sticky="news")

        self._race_button: Button = Button(self, text=RaceFrame.StartRacingText)
        self._race_button.grid(row=5, column=0, sticky="news")
        self._race_button.bind("<Button-1>", self._race_clicked)

        for row in range(self.grid_size()[1]):
            self.grid_rowconfigure(row, weight=0, minsize=1)

        for column in range(self.grid_size()[0]):
            self.grid_columnconfigure(column, weight=1, minsize=1)

    def _start_race(self) -> None:
        while self._race_loop_running:
            if not self._nt_browser.racing:
                self._nt_browser.race(
                    self._wpm_scale.get(),
                    self._accuracy_scale.get()
                )
            sleep(1)

    def _race_clicked(self, event: Event) -> None:
        if self._nt_browser.racing:
            if self._race_button["text"] == RaceFrame.StartRacingText:
                messagebox.showwarning(
                    "Warning",
                    "You are currently racing.\n\nWait for the race to finish."
                )

            self._race_loop_running = False
            self._race_button.config(text=RaceFrame.StartRacingText)
        else:
            self._race_loop_running = True
            self._race_button.config(text=RaceFrame.StopRacingText)
            Thread(target=self._start_race).start()



class UI:
    def __init__(self, nt_browser: NtBrowser) -> None:
        self._nt_browser: NtBrowser = nt_browser

        window: Tk = ThemedTk(theme="Plastik")
        window.title(APP_NAME)
        window.iconbitmap(str(APP_ICON))

        login_frame: LoginFrame = LoginFrame(window, self._nt_browser)
        race_frame: RaceFrame = RaceFrame(window, self._nt_browser)

        for frame in [
            login_frame,
            race_frame
        ]:
            frame.grid(row=0, column=0, padx=5, pady=5, sticky="news")

        for row in range(window.grid_size()[1]):
            window.grid_rowconfigure(row, weight=1, minsize=1)

        for column in range(window.grid_size()[0]):
            window.grid_columnconfigure(column, weight=1, minsize=1)

        login_frame.subscribe_to_login(lambda: race_frame.tkraise())
        login_frame.tkraise()

        # Center display:
        # window.eval("tk::PlaceWindow . center")  <- Breaks pyinstaller task bar icon.
        window.update_idletasks()
        width: int = window.winfo_width()
        height: int = window.winfo_height()
        screen_width: int = window.winfo_screenwidth()
        screen_height: int = window.winfo_screenheight()
        window_x: int = (screen_width - width) // 2
        window_y: int = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{window_x}+{window_y}")

        try:
            window.mainloop()
        finally:
            self._nt_browser.quit()

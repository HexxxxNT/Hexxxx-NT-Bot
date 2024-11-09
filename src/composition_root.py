
from src.nt_browser import NtBrowser
from src.ui import UI


if __name__ == "__main__":
    UI(NtBrowser())

    """with NtBrowser() as browser:
        browser.login("username", "password")
        while True:
            browser.race(100)"""

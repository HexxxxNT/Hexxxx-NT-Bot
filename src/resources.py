from pathlib import Path
from typing import Final

ROOT_DIR: Final[Path] = Path(__file__).parent.parent.resolve()
RES_DIR: Final[Path] = ROOT_DIR / "res"

APP_ICON: Final[Path] = RES_DIR / "icon.ico"
ANDROID: Final[Path] = RES_DIR / "android.png"

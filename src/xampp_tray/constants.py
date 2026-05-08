import os

from xampp_tray import VERSION as _VERSION

VERSION: str = _VERSION

LAMPP_PATH: str = "/opt/lampp/lampp"


def _resolve_icon_path() -> str:
    installed = "/usr/share/xampp-tray/assets/xampp.png"
    if os.path.exists(installed):
        return installed
    dev = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "xampp.png")
    )
    return dev


ICON_PATH: str = _resolve_icon_path()

DATA_DIR: str = os.path.expanduser("~/.local/share/xampp-tray")
LOG_DIR: str = os.path.join(DATA_DIR, "logs")
LOG_FILE: str = os.path.join(LOG_DIR, "xampp-tray.log")
HISTORY_FILE: str = os.path.join(DATA_DIR, "history.json")
CONFIG_FILE: str = os.path.join(DATA_DIR, "config.json")

HISTORY_MAX: int = 20
POLL_INTERVAL: int = 5
LOG_MAX_BYTES: int = 5 * 1024 * 1024
LOG_BACKUP_COUNT: int = 3
AUTOSTART_DELAY: float = 2.0

import json
import logging
import os
from typing import Any

from xampp_tray.constants import CONFIG_FILE, DATA_DIR

logger = logging.getLogger(__name__)

_DEFAULTS: dict[str, Any] = {
    "autostart_app": False,
    "autostart_apache": False,
    "autostart_mysql": False,
}


class ConfigManager:
    def __init__(self, path: str = CONFIG_FILE) -> None:
        self._path = path
        self._data: dict[str, Any] = dict(_DEFAULTS)

    def load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path) as f:
                self._data.update(json.load(f))
        except Exception:
            logger.warning("Falha ao carregar config, usando padrões.")

    def save(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def toggle(self, key: str) -> bool:
        new_val = not self._data.get(key, False)
        self._data[key] = new_val
        return new_val

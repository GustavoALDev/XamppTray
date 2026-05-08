import json
import logging
import os
from datetime import datetime
from typing import TypedDict

from xampp_tray.constants import DATA_DIR, HISTORY_FILE, HISTORY_MAX

logger = logging.getLogger(__name__)


class HistoryEntry(TypedDict):
    time: str
    title: str
    message: str


class HistoryManager:
    def __init__(self, path: str = HISTORY_FILE, max_entries: int = HISTORY_MAX) -> None:
        self._path = path
        self._max = max_entries
        self._entries: list[HistoryEntry] = []

    def load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path) as f:
                self._entries = json.load(f)
        except Exception:
            logger.warning("Falha ao carregar histórico.")

    def save(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._entries, f, ensure_ascii=False, indent=2)

    def add(self, title: str, message: str) -> None:
        entry: HistoryEntry = {
            "time": datetime.now().strftime("%d/%m %H:%M"),
            "title": title,
            "message": message,
        }
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries.pop(0)
        self.save()

    def recent(self, n: int = 10) -> list[HistoryEntry]:
        return list(reversed(self._entries[-n:]))

    def is_empty(self) -> bool:
        return len(self._entries) == 0

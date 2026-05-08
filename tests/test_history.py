import json
from pathlib import Path

import pytest

from xampp_tray.history import HistoryManager


@pytest.fixture
def hist(tmp_path: Path) -> HistoryManager:
    return HistoryManager(path=str(tmp_path / "history.json"), max_entries=5)


def test_empty_on_init(hist: HistoryManager) -> None:
    assert hist.is_empty()


def test_add_entry(hist: HistoryManager) -> None:
    hist.add("XAMPP", "Serviços iniciados.")
    assert not hist.is_empty()


def test_recent_returns_reversed(hist: HistoryManager) -> None:
    hist.add("A", "first")
    hist.add("B", "second")
    recent = hist.recent(2)
    assert recent[0]["title"] == "B"
    assert recent[1]["title"] == "A"


def test_max_entries_rotation(hist: HistoryManager) -> None:
    for i in range(7):
        hist.add("T", str(i))
    recent = hist.recent(10)
    assert len(recent) == 5


def test_save_and_load(tmp_path: Path) -> None:
    path = str(tmp_path / "history.json")
    h1 = HistoryManager(path=path)
    h1.add("XAMPP", "teste")
    h1.save()

    h2 = HistoryManager(path=path)
    h2.load()
    assert not h2.is_empty()
    assert h2.recent(1)[0]["title"] == "XAMPP"


def test_load_gracefully_handles_corrupt_file(tmp_path: Path) -> None:
    path = tmp_path / "history.json"
    path.write_text("[ bad json")
    h = HistoryManager(path=str(path))
    h.load()
    assert h.is_empty()

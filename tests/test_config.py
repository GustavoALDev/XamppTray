import json
import os
from pathlib import Path

import pytest

from xampp_tray.config import ConfigManager


@pytest.fixture
def cfg(tmp_path: Path) -> ConfigManager:
    return ConfigManager(path=str(tmp_path / "config.json"))


def test_defaults_before_load(cfg: ConfigManager) -> None:
    assert cfg.get("autostart_app") is False
    assert cfg.get("autostart_apache") is False
    assert cfg.get("autostart_mysql") is False


def test_load_from_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"autostart_app": True, "autostart_apache": True}))
    cfg = ConfigManager(path=str(config_file))
    cfg.load()
    assert cfg.get("autostart_app") is True
    assert cfg.get("autostart_apache") is True
    assert cfg.get("autostart_mysql") is False


def test_save_and_reload(cfg: ConfigManager, tmp_path: Path) -> None:
    cfg.set("autostart_app", True)
    cfg.save()
    cfg2 = ConfigManager(path=str(tmp_path / "config.json"))
    cfg2.load()
    assert cfg2.get("autostart_app") is True


def test_toggle(cfg: ConfigManager) -> None:
    assert cfg.toggle("autostart_apache") is True
    assert cfg.get("autostart_apache") is True
    assert cfg.toggle("autostart_apache") is False


def test_load_gracefully_handles_corrupt_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text("{ not valid json }")
    cfg = ConfigManager(path=str(config_file))
    cfg.load()
    assert cfg.get("autostart_app") is False


def test_missing_file_loads_defaults(cfg: ConfigManager) -> None:
    cfg.load()
    assert cfg.get("autostart_app") is False

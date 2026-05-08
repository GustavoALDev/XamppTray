import os

import pytest
from PIL import Image

from xampp_tray.icon import _dot_color, build_icon
from xampp_tray.service import ServiceState

ICON_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "assets", "xampp.png")
)


@pytest.mark.skipif(not os.path.exists(ICON_PATH), reason="assets/xampp.png not found")
def test_build_icon_returns_image() -> None:
    img = build_icon(ICON_PATH, ServiceState.RUNNING, ServiceState.STOPPED)
    assert isinstance(img, Image.Image)
    assert img.size == (48, 48)
    assert img.mode == "RGBA"


def test_dot_color_running() -> None:
    r, g, b, a = _dot_color(ServiceState.RUNNING)
    assert g > r and g > b


def test_dot_color_stopped() -> None:
    r, g, b, a = _dot_color(ServiceState.STOPPED)
    assert r > g and r > b


def test_dot_color_transitioning() -> None:
    starting = _dot_color(ServiceState.STARTING)
    stopping = _dot_color(ServiceState.STOPPING)
    assert starting == stopping
    r, g, b, a = starting
    assert r > 200 and g > 150

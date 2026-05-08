from PIL import Image, ImageDraw

from xampp_tray.service import ServiceState


def _dot_color(state: ServiceState) -> tuple[int, int, int, int]:
    if state == ServiceState.RUNNING:
        return (76, 175, 80, 255)
    elif state == ServiceState.STOPPED:
        return (244, 67, 54, 255)
    return (255, 193, 7, 255)


def build_icon(icon_path: str, apache: ServiceState, mysql: ServiceState) -> Image.Image:
    base = Image.open(icon_path).convert("RGBA").resize((48, 48))
    draw = ImageDraw.Draw(base)
    draw.ellipse([2, 34, 14, 46], fill=_dot_color(apache), outline=(0, 0, 0, 180))
    draw.ellipse([34, 34, 46, 46], fill=_dot_color(mysql), outline=(0, 0, 0, 180))
    return base

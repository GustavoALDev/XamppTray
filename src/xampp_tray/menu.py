from collections.abc import Callable
from typing import Any

from pystray import Menu, MenuItem

from xampp_tray.history import HistoryManager
from xampp_tray.service import ServiceState, ServiceStatus


def _status_label(service: str, state: ServiceState) -> str:
    if state == ServiceState.RUNNING:
        return f"\U0001f7e2 {service.capitalize()}: Running"
    elif state == ServiceState.STOPPED:
        return f"\U0001f534 {service.capitalize()}: Stopped"
    elif state == ServiceState.STARTING:
        return f"\U0001f7e1 {service.capitalize()}: Starting..."
    return f"\U0001f7e1 {service.capitalize()}: Stopping..."


def _history_items(history: HistoryManager) -> tuple[MenuItem, ...]:
    if history.is_empty():
        return (MenuItem("(sem registros)", lambda *_: None, enabled=False),)
    items = []
    for entry in history.recent():
        label = f"[{entry['time']}] {entry['title']}: {entry['message'][:50]}"
        items.append(MenuItem(label, lambda *_: None, enabled=False))
    return tuple(items)


def build_menu(
    status: ServiceStatus,
    history: HistoryManager,
    config_get: Callable[[str], Any],
    on_start: Callable[..., None],
    on_stop: Callable[..., None],
    on_restart: Callable[..., None],
    on_check_status: Callable[..., None],
    on_dashboard: Callable[..., None],
    on_gui: Callable[..., None],
    on_toggle_autostart_app: Callable[..., None],
    on_toggle_autostart_apache: Callable[..., None],
    on_toggle_autostart_mysql: Callable[..., None],
    on_uninstall: Callable[..., None],
    on_quit: Callable[..., None],
) -> Menu:
    return Menu(
        MenuItem(_status_label("apache", status.apache), lambda *_: None, enabled=False),
        MenuItem(_status_label("mysql", status.mysql), lambda *_: None, enabled=False),
        Menu.SEPARATOR,
        MenuItem("Start XAMPP", on_start),
        MenuItem("Stop XAMPP", on_stop),
        MenuItem("Restart XAMPP", on_restart),
        Menu.SEPARATOR,
        MenuItem(
            "Configurações   ",
            Menu(
                MenuItem(
                    "Iniciar com o OS",
                    on_toggle_autostart_app,
                    checked=lambda item: config_get("autostart_app"),
                ),
                Menu.SEPARATOR,
                MenuItem(
                    "Auto-start Servidores ",
                    Menu(
                        MenuItem(
                            "Apache",
                            on_toggle_autostart_apache,
                            checked=lambda item: config_get("autostart_apache"),
                        ),
                        MenuItem(
                            "MySQL",
                            on_toggle_autostart_mysql,
                            checked=lambda item: config_get("autostart_mysql"),
                        ),
                    ),
                ),
            ),
        ),
        Menu.SEPARATOR,
        MenuItem("Status", on_check_status),
        MenuItem("Open Dashboard", on_dashboard),
        MenuItem("Open XAMPP GUI", on_gui),
        Menu.SEPARATOR,
        MenuItem("Historico", Menu(lambda: _history_items(history))),
        Menu.SEPARATOR,
        MenuItem("Desinstalar", on_uninstall),
        Menu.SEPARATOR,
        MenuItem("Sair", on_quit),
    )

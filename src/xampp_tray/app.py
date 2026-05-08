import logging
import os
import shutil
import subprocess
import threading
import time
import webbrowser
from logging.handlers import RotatingFileHandler

from pystray import Icon

from xampp_tray.config import ConfigManager
from xampp_tray.constants import (
    AUTOSTART_DELAY,
    ICON_PATH,
    LAMPP_PATH,
    LOG_BACKUP_COUNT,
    LOG_FILE,
    LOG_MAX_BYTES,
)
from xampp_tray.history import HistoryManager
from xampp_tray.icon import build_icon
from xampp_tray.menu import build_menu
from xampp_tray.notifications import notify
from xampp_tray.service import ServiceState, ServiceStatus, XamppService
from xampp_tray.status import StatusPoller

logger = logging.getLogger(__name__)


class TrayApp:
    def __init__(
        self,
        lampp_path: str = LAMPP_PATH,
        icon_path: str = ICON_PATH,
    ) -> None:
        self._icon_path = icon_path
        self._service = XamppService(lampp_path)
        self._config = ConfigManager()
        self._history = HistoryManager()
        self._status = ServiceStatus(
            apache=ServiceState.STOPPED, mysql=ServiceState.STOPPED
        )
        self._lock = threading.Lock()
        self._tray: Icon | None = None
        self._poller: StatusPoller | None = None

    def run(self) -> None:
        if not os.path.exists(self._icon_path):
            raise FileNotFoundError(f"Ícone não encontrado: {self._icon_path}")

        self._setup_logging()
        self._config.load()
        self._history.load()

        output = self._service.status(silent=True)
        self._status = self._service.parse_status(output)

        self._poller = StatusPoller(
            service=self._service,
            on_change=self._on_status_change,
        )
        self._poller.update(self._status)
        self._poller.start()

        if self._config.get("autostart_apache") or self._config.get("autostart_mysql"):
            threading.Thread(target=self._auto_start_services, daemon=True).start()

        image = build_icon(self._icon_path, self._status.apache, self._status.mysql)
        self._tray = Icon("XAMPP", image, "XAMPP Control", self._make_menu())
        self._tray.run()

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_status_change(self, new_status: ServiceStatus) -> None:
        with self._lock:
            self._status = new_status
        self._refresh()

    def _refresh(self) -> None:
        if self._tray is None:
            return
        with self._lock:
            status = self._status
        self._tray.icon = build_icon(self._icon_path, status.apache, status.mysql)
        self._tray.menu = self._make_menu()

    def _make_menu(self):  # type: ignore[no-untyped-def]
        with self._lock:
            status = self._status
        return build_menu(
            status=status,
            history=self._history,
            config_get=self._config.get,
            on_start=self._start,
            on_stop=self._stop,
            on_restart=self._restart,
            on_check_status=self._check_status,
            on_dashboard=self._open_dashboard,
            on_gui=self._open_gui,
            on_toggle_autostart_app=self._toggle_autostart_app,
            on_toggle_autostart_apache=self._toggle_autostart_service("apache"),
            on_toggle_autostart_mysql=self._toggle_autostart_service("mysql"),
            on_uninstall=self._uninstall,
            on_quit=self._quit,
        )

    # ── XAMPP actions ─────────────────────────────────────────────────────────

    def _set_transition(self, apache: ServiceState, mysql: ServiceState) -> None:
        with self._lock:
            self._status = ServiceStatus(apache=apache, mysql=mysql)
        if self._poller:
            self._poller.update(self._status)
        self._refresh()

    def _post_action(self, output: str, label: str) -> None:
        status_out = self._service.status(silent=True)
        new_status = self._service.parse_status(status_out)
        with self._lock:
            self._status = new_status
        if self._poller:
            self._poller.update(new_status)
        self._notify(label, output.strip() or f"Operação concluída.")
        self._refresh()

    def _start(self, icon: Icon, item: object) -> None:
        self._notify("XAMPP", "Iniciando serviços...")
        self._set_transition(ServiceState.STARTING, ServiceState.STARTING)
        output = self._service.start()
        self._post_action(output, "XAMPP")

    def _stop(self, icon: Icon, item: object) -> None:
        self._notify("XAMPP", "Parando serviços...")
        self._set_transition(ServiceState.STOPPING, ServiceState.STOPPING)
        output = self._service.stop()
        self._post_action(output, "XAMPP")

    def _restart(self, icon: Icon, item: object) -> None:
        self._notify("XAMPP", "Reiniciando serviços...")
        self._set_transition(ServiceState.STARTING, ServiceState.STARTING)
        output = self._service.restart()
        self._post_action(output, "XAMPP")

    def _check_status(self, icon: Icon, item: object) -> None:
        output = self._service.status()
        self._notify("XAMPP Status", output.strip() or "Sem resposta do comando.")

    # ── Settings ──────────────────────────────────────────────────────────────

    def _toggle_autostart_app(self, icon: Icon, item: object) -> None:
        enabled = self._config.toggle("autostart_app")
        self._config.save()
        if enabled:
            self._install_desktop_entries()
            self._notify("Configuração", "Autostart do aplicativo ativado.")
        else:
            self._remove_desktop_entries()
            self._notify("Configuração", "Autostart do aplicativo desativado.")
        self._refresh()

    def _desktop_entry_content(self) -> str:
        exec_cmd = "xampp-tray" if shutil.which("xampp-tray") else (
            f"env PYTHONPATH={os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))}/src"
            f" python3 -m xampp_tray"
        )
        return (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=XAMPP Tray\n"
            "GenericName=XAMPP Control\n"
            "Comment=Control XAMPP from the system tray\n"
            f"Exec={exec_cmd}\n"
            f"Icon={self._icon_path}\n"
            "Terminal=false\n"
            "StartupNotify=false\n"
            "Categories=Development;WebDevelopment;\n"
            "Keywords=xampp;apache;mysql;server;php;\n"
        )

    def _install_desktop_entries(self) -> None:
        content = self._desktop_entry_content()

        autostart_path = os.path.expanduser("~/.config/autostart/xampp-tray.desktop")
        app_menu_path = os.path.expanduser("~/.local/share/applications/xampp-tray.desktop")
        desktop_path = os.path.expanduser("~/Desktop/xampp-tray.desktop")

        for path in (autostart_path, app_menu_path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)

        if os.path.isdir(os.path.expanduser("~/Desktop")):
            with open(desktop_path, "w") as f:
                f.write(content)
            os.chmod(desktop_path, 0o755)

    def _remove_desktop_entries(self) -> None:
        for path in (
            os.path.expanduser("~/.config/autostart/xampp-tray.desktop"),
            os.path.expanduser("~/.local/share/applications/xampp-tray.desktop"),
            os.path.expanduser("~/Desktop/xampp-tray.desktop"),
        ):
            if os.path.exists(path):
                os.remove(path)

    def _toggle_autostart_service(self, service: str):  # type: ignore[no-untyped-def]
        def _toggle(icon: Icon, item: object) -> None:
            enabled = self._config.toggle(f"autostart_{service}")
            self._config.save()
            state = "ativado" if enabled else "desativado"
            self._notify("Configuração", f"Auto-start do {service.capitalize()} {state}.")
            self._refresh()
        return _toggle

    # ── Other menu actions ────────────────────────────────────────────────────

    def _open_dashboard(self, icon: Icon, item: object) -> None:
        webbrowser.open("http://localhost")

    def _open_gui(self, icon: Icon, item: object) -> None:
        gui_paths = [
            "/opt/lampp/manager-linux-x64.run",
            "/opt/lampp/manager-linux.run",
        ]
        for path in gui_paths:
            if os.path.exists(path):
                subprocess.Popen(["/usr/bin/pkexec", path])
                return
        self._notify("XAMPP", "Painel gráfico não encontrado em /opt/lampp/.")

    def _uninstall(self, icon: Icon, item: object) -> None:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        confirmed = messagebox.askyesno(
            "Desinstalar XAMPP Tray App",
            "Tem certeza que deseja remover completamente o XAMPP Tray App?",
        )
        root.destroy()

        if not confirmed:
            return

        self._notify("Desinstalação", "Iniciando processo de desinstalação...")

        if self._is_deb_install():
            # apt purge aciona prerm (mata processo, remove sudoers) e
            # postrm purge (remove user caches de todos os usuários em /home)
            subprocess.Popen(["/usr/bin/pkexec", "apt-get", "purge", "-y", "xampp-tray"])
        else:
            # Source install: remove apenas os arquivos do usuário atual
            self._remove_desktop_entries()
            user_data = os.path.expanduser("~/.local/share/xampp-tray")
            if os.path.exists(user_data):
                shutil.rmtree(user_data)

        if self._tray:
            self._tray.stop()

    @staticmethod
    def _is_deb_install() -> bool:
        result = subprocess.run(
            ["dpkg", "-l", "xampp-tray"],
            capture_output=True,
        )
        return result.returncode == 0

    def _quit(self, icon: Icon, item: object) -> None:
        if self._poller:
            self._poller.stop()
        icon.stop()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _notify(self, title: str, message: str) -> None:
        notify(title, message)
        self._history.add(title, message)
        self._refresh()

    def _auto_start_services(self) -> None:
        time.sleep(AUTOSTART_DELAY)
        logger.info("Iniciando auto-start dos serviços configurados...")
        if self._config.get("autostart_apache") and self._config.get("autostart_mysql"):
            self._service.start()
        else:
            if self._config.get("autostart_apache"):
                self._service.start_apache()
            if self._config.get("autostart_mysql"):
                self._service.start_mysql()
        output = self._service.status(silent=True)
        new_status = self._service.parse_status(output)
        with self._lock:
            self._status = new_status
        if self._poller:
            self._poller.update(new_status)
        self._refresh()

    @staticmethod
    def _setup_logging() -> None:
        import sys
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        handler = RotatingFileHandler(
            LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT
        )
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler(sys.stderr)])

        def _excepthook(
            exc_type: type[BaseException],
            exc_value: BaseException,
            exc_tb: object,
        ) -> None:
            if issubclass(exc_type, KeyboardInterrupt):
                return
            logging.critical("Exceção não capturada", exc_info=(exc_type, exc_value, exc_tb))

        sys.excepthook = _excepthook
        logging.info("--- Sistema de logging iniciado ---")

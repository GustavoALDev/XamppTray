import os
import sys

VERSION = "2.1.2"

# Adiciona o diretorio lib ao path se existir (para o pacote .deb)
lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
if os.path.exists(lib_path):
    sys.path.insert(0, lib_path)

import json
import threading
import subprocess
import webbrowser
import logging
import time
from logging.handlers import RotatingFileHandler
from datetime import datetime
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "xampp.png")
HISTORY_DIR = os.path.expanduser("~/.local/share/xampp-tray")
LOG_DIR = os.path.join(HISTORY_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "xampp-tray.log")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")
CONFIG_FILE = os.path.join(HISTORY_DIR, "config.json")
HISTORY_MAX = 20
POLL_INTERVAL = 5  # seconds

# Shared state
_status = {"apache": "stopped", "mysql": "stopped"}
_status_lock = threading.Lock()
_history: list[dict] = []
_config = {
    "autostart_app": False,
    "autostart_apache": False,
    "autostart_mysql": False
}
_tray_icon = None

def _setup_logging():
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler(sys.stderr)])
        
        def _excepthook(exc_type, exc_value, exc_tb):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_tb)
                return
            logging.critical("Exceção não capturada", exc_info=(exc_type, exc_value, exc_tb))
        sys.excepthook = _excepthook
        logging.info("--- Sistema de logging iniciado ---")
    except Exception as e:
        print(f"Erro ao configurar logging: {e}", file=sys.stderr)


# ── Configuration & History ───────────────────────────────────────────────────

def load_config():
    global _config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                _config.update(data)
        except Exception:
            pass

def save_config():
    os.makedirs(HISTORY_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(_config, f, ensure_ascii=False, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_history():
    os.makedirs(HISTORY_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(_history, f, ensure_ascii=False, indent=2)

def notify(title, message):
    msg = message or "Sem resposta do comando."
    subprocess.run(["notify-send", title, msg], capture_output=True)
    entry = {"time": datetime.now().strftime("%d/%m %H:%M"), "title": title, "message": msg}
    _history.append(entry)
    if len(_history) > HISTORY_MAX:
        _history.pop(0)
    save_history()
    _rebuild_menu()


# ── Icon generation ───────────────────────────────────────────────────────────

def _dot_color(state: str) -> tuple:
    if state == "running":
        return (76, 175, 80, 255)
    elif state == "stopped":
        return (244, 67, 54, 255)
    else:
        return (255, 193, 7, 255)  # Yellow/Amber for transition

def build_icon(apache: bool, mysql: bool) -> Image.Image:
    base = Image.open(ICON_PATH).convert("RGBA").resize((48, 48))
    draw = ImageDraw.Draw(base)
    # Apache dot — bottom-left
    draw.ellipse([2, 34, 14, 46], fill=_dot_color(apache), outline=(0, 0, 0, 180))
    # MySQL dot — bottom-right
    draw.ellipse([34, 34, 46, 46], fill=_dot_color(mysql), outline=(0, 0, 0, 180))
    return base


# ── Status polling ────────────────────────────────────────────────────────────

def _parse_status(output: str) -> dict:
    lower = output.lower()
    return {
        "apache": "running" if "apache is running" in lower else "stopped",
        "mysql": "running" if "mysql is running" in lower else "stopped",
    }

def _poll_loop():
    while True:
        with _status_lock:
            is_transitioning = any(s in ["starting", "stopping"] for s in _status.values())
        
        if not is_transitioning:
            # Para polling de status, usamos sudo mas de forma silenciosa.
            # Se o sudo pedir senha aqui, o polling vai travar, por isso usamos -n (non-interactive)
            output = run_command("sudo -n /opt/lampp/lampp status", silent=True)
            new_status = _parse_status(output)
            changed = False
            with _status_lock:
                if new_status != _status:
                    _status.update(new_status)
                    changed = True
            if changed and _tray_icon:
                _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
                _rebuild_menu()
        threading.Event().wait(POLL_INTERVAL)


# ── Menu ──────────────────────────────────────────────────────────────────────

def _status_label(service: str) -> str:
    state = _status.get(service, "stopped")
    if state == "running":
        dot = "🟢 "
        text = "Running"
    elif state == "stopped":
        dot = "🔴 "
        text = "Stopped"
    else:
        dot = "🟡 "
        text = "Starting..." if state == "starting" else "Stopping..."
    return f"{dot}{service.capitalize()}: {text}"

def _history_items():
    if not _history:
        return [MenuItem("(sem registros)", lambda *_: None, enabled=False)]
    items = []
    for entry in reversed(_history[-10:]):
        label = f"[{entry['time']}] {entry['title']}: {entry['message'][:50]}"
        items.append(MenuItem(label, lambda *_: None, enabled=False))
    return items

def uninstall_app(icon, item):
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    ans = messagebox.askyesno("Desinstalar XAMPP Tray App", 
                              "Tem certeza que deseja remover completamente o XAMPP Tray App e todos os seus arquivos?")
    root.destroy()
    
    if ans:
        script_path = "/usr/share/xampp-tray/uninstall-clean.sh"
        if not os.path.exists(script_path):
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uninstall-clean.sh")
            
        cmd = f"pkexec bash {script_path}"
        notify("Desinstalação", "Iniciando processo de desinstalação...")
        subprocess.Popen(cmd, shell=True)

def _build_menu():
    return Menu(
        MenuItem(_status_label("apache"), lambda *_: None, enabled=False),
        MenuItem(_status_label("mysql"), lambda *_: None, enabled=False),
        Menu.SEPARATOR,
        MenuItem("Start XAMPP", start_xampp),
        MenuItem("Stop XAMPP", stop_xampp),
        MenuItem("Restart XAMPP", restart_xampp),
        Menu.SEPARATOR,
        MenuItem("Configurações\u2003\u2003\u2003", Menu(
            MenuItem("Iniciar com o OS", toggle_autostart_app, checked=lambda item: _config.get("autostart_app", False)),
            Menu.SEPARATOR,
            MenuItem("Auto-start Servidores\u2003", Menu(
                MenuItem("Apache", toggle_autostart_service("apache"), checked=lambda item: _config.get("autostart_apache", False)),
                MenuItem("MySQL", toggle_autostart_service("mysql"), checked=lambda item: _config.get("autostart_mysql", False)),
            ))
        )),
        Menu.SEPARATOR,
        MenuItem("Status", check_status),
        MenuItem("Open Dashboard", open_dashboard),
        MenuItem("Open XAMPP GUI", open_gui),
        Menu.SEPARATOR,
        MenuItem("Historico", Menu(lambda: tuple(_history_items()))),
        Menu.SEPARATOR,
        MenuItem("Desinstalar", uninstall_app),
        Menu.SEPARATOR,
        MenuItem("Sair", quit_app),
    )


def _rebuild_menu():
    if _tray_icon:
        _tray_icon.menu = _build_menu()


# ── Commands ──────────────────────────────────────────────────────────────────

def run_command(command, silent=False):
    try:
        # Se o comando usa sudo, tentamos rodar. Se falhar por falta de permissao (exit code 1 ou similar),
        # e estivermos em um contexto que permite GUI, poderiamos usar pkexec.
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Se falhou e era um comando sudo, tenta com pkexec se nao for silencioso
        if result.returncode != 0 and command.startswith("sudo") and not silent:
            logging.info(f"Comando sudo falhou (code {result.returncode}), tentando pkexec...")
            pk_cmd = command.replace("sudo", "pkexec", 1)
            result = subprocess.run(pk_cmd, shell=True, capture_output=True, text=True)

        if not silent:
            logging.info(f"Executando: {command} (Exit Code: {result.returncode})")
            if result.stderr:
                logging.warning(f"Mensagem do comando: {result.stderr.strip()}")
        return result.stdout or result.stderr
    except Exception as e:
        logging.error(f"Falha fatal ao executar {command}: {e}")
        return str(e)

def start_xampp(icon, item):
    global _status
    notify("XAMPP", "Iniciando servicos...")
    with _status_lock:
        _status["apache"] = "starting"
        _status["mysql"] = "starting"
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    
    # Usamos sudo mas o run_command vai tentar pkexec se o sudo falhar silenciosamente
    output = run_command("sudo /opt/lampp/lampp start")
    
    status_output = run_command("sudo -n /opt/lampp/lampp status", silent=True)
    new_status = _parse_status(status_output)
    with _status_lock:
        _status.update(new_status)
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    notify("XAMPP", output.strip() or "Serviços iniciados.")

def stop_xampp(icon, item):
    global _status
    notify("XAMPP", "Parando servicos...")
    with _status_lock:
        _status["apache"] = "stopping"
        _status["mysql"] = "stopping"
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    
    output = run_command("sudo /opt/lampp/lampp stop")
    
    status_output = run_command("sudo -n /opt/lampp/lampp status", silent=True)
    new_status = _parse_status(status_output)
    with _status_lock:
        _status.update(new_status)
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    notify("XAMPP", output.strip() or "Serviços parados.")

def restart_xampp(icon, item):
    global _status
    notify("XAMPP", "Reiniciando servicos...")
    with _status_lock:
        _status["apache"] = "starting"
        _status["mysql"] = "starting"
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    
    output = run_command("sudo /opt/lampp/lampp restart")
    
    status_output = run_command("sudo -n /opt/lampp/lampp status", silent=True)
    new_status = _parse_status(status_output)
    with _status_lock:
        _status.update(new_status)
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    notify("XAMPP", output.strip() or "Serviços reiniciados.")

def check_status(icon, item):
    output = run_command("sudo -n /opt/lampp/lampp status")
    notify("XAMPP Status", output.strip() or "Sem resposta do comando.")

def open_dashboard(icon, item):
    webbrowser.open("http://localhost")

def open_gui(icon, item):
    gui_paths = [
        "/opt/lampp/manager-linux-x64.run",
        "/opt/lampp/manager-linux.run",
    ]
    for path in gui_paths:
        if os.path.exists(path):
            # Para o GUI, pkexec é melhor que sudo direto
            subprocess.Popen(["pkexec", path])
            return
    notify("XAMPP", "Painel grafico do XAMPP nao encontrado em /opt/lampp/.")

def toggle_autostart_app(icon, item):
    global _config
    _config["autostart_app"] = not _config["autostart_app"]
    save_config()
    
    autostart_path = os.path.expanduser("~/.config/autostart/xampp-tray.desktop")
    if _config["autostart_app"]:
        os.makedirs(os.path.dirname(autostart_path), exist_ok=True)
        # Caminhos possiveis para o arquivo desktop
        desktop_sources = [
            "/usr/share/applications/xampp-tray.desktop",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "xampp-tray.desktop")
        ]
        
        found = False
        for src in desktop_sources:
            if os.path.exists(src):
                import shutil
                shutil.copy(src, autostart_path)
                found = True
                break
        
        if not found:
            # Fallback manual
            with open(autostart_path, "w") as f:
                f.write(f"[Desktop Entry]\nType=Application\nName=XAMPP Tray\nExec=python3 {os.path.abspath(__file__)}\nIcon={ICON_PATH}\nTerminal=false\n")
        
        logging.info("Autostart do aplicativo ativado.")
        notify("Configuração", "Autostart do aplicativo ativado.")
    else:
        if os.path.exists(autostart_path):
            os.remove(autostart_path)
        logging.info("Autostart do aplicativo desativado.")
        notify("Configuração", "Autostart do aplicativo desativado.")
    _rebuild_menu()

def toggle_autostart_service(service):
    def _toggle(icon, item):
        global _config
        key = f"autostart_{service}"
        _config[key] = not _config.get(key, False)
        save_config()
        logging.info(f"Auto-start do {service} {'ativado' if _config[key] else 'desativado'}.")
        notify("Configuração", f"Auto-start do {service.capitalize()} {'ativado' if _config[key] else 'desativado'}.")
        _rebuild_menu()
    return _toggle

def quit_app(icon, item):
    icon.stop()


# ── Setup ─────────────────────────────────────────────────────────────────────

def setup():
    global _tray_icon, _history

    if not os.path.exists(ICON_PATH):
        print(f"Erro: icone nao encontrado em {ICON_PATH}")
        return

    _setup_logging()
    load_config()
    _history = load_history()

    # Initial status check - silencioso para evitar pedir senha no setup se nao estiver no sudoers
    output = run_command("sudo -n /opt/lampp/lampp status", silent=True)
    _status.update(_parse_status(output))

    # Auto-start services if configured
    if _config.get("autostart_apache") or _config.get("autostart_mysql"):
        def _auto_start_job():
            # Aguarda o sistema carregar o ambiente grafico
            time.sleep(2)
            
            logging.info("Iniciando auto-start dos serviços configurados...")
            
            # Se ambos estiverem ativos, podemos tentar 'sudo /opt/lampp/lampp start'
            # que inicia tudo e pede senha uma vez só.
            if _config.get("autostart_apache") and _config.get("autostart_mysql"):
                run_command("sudo /opt/lampp/lampp start")
            else:
                if _config.get("autostart_apache"):
                    run_command("sudo /opt/lampp/lampp startapache")
                if _config.get("autostart_mysql"):
                    run_command("sudo /opt/lampp/lampp startmysql")
            
            # Refresh status
            final_status = run_command("sudo -n /opt/lampp/lampp status", silent=True)
            with _status_lock:
                _status.update(_parse_status(final_status))
            if _tray_icon:
                _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
                _rebuild_menu()
        
        threading.Thread(target=_auto_start_job, daemon=True).start()

    image = build_icon(_status["apache"], _status["mysql"])

    _tray_icon = Icon("XAMPP", image, "XAMPP Control", _build_menu())

    # Background polling thread
    poll_thread = threading.Thread(target=_poll_loop, daemon=True)
    poll_thread.start()

    _tray_icon.run()


if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("\nEncerrando o XAMPP Tray App.")

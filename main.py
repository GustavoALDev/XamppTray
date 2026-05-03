import os
import json
import threading
import subprocess
import webbrowser
from datetime import datetime
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "xampp.png")
HISTORY_DIR = os.path.expanduser("~/.local/share/xampp-tray")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")
HISTORY_MAX = 20
POLL_INTERVAL = 5  # seconds

# Shared state
_status = {"apache": "stopped", "mysql": "stopped"}
_status_lock = threading.Lock()
_history: list[dict] = []
_tray_icon = None


# ── Notification history ──────────────────────────────────────────────────────

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
            output = run_command("sudo /opt/lampp/lampp status")
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

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout or result.stderr
    except Exception as e:
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
    
    output = run_command("sudo /opt/lampp/lampp start")
    
    status_output = run_command("sudo /opt/lampp/lampp status")
    new_status = _parse_status(status_output)
    with _status_lock:
        _status.update(new_status)
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    notify("XAMPP", output.strip() or "Sem resposta do comando.")

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
    
    status_output = run_command("sudo /opt/lampp/lampp status")
    new_status = _parse_status(status_output)
    with _status_lock:
        _status.update(new_status)
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    notify("XAMPP", output.strip() or "Sem resposta do comando.")

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
    
    status_output = run_command("sudo /opt/lampp/lampp status")
    new_status = _parse_status(status_output)
    with _status_lock:
        _status.update(new_status)
    _rebuild_menu()
    if _tray_icon:
        _tray_icon.icon = build_icon(_status["apache"], _status["mysql"])
    notify("XAMPP", output.strip() or "Sem resposta do comando.")

def check_status(icon, item):
    output = run_command("sudo /opt/lampp/lampp status")
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
            subprocess.Popen(["sudo", path])
            return
    notify("XAMPP", "Painel grafico do XAMPP nao encontrado em /opt/lampp/.")

def quit_app(icon, item):
    icon.stop()


# ── Setup ─────────────────────────────────────────────────────────────────────

def setup():
    global _tray_icon, _history

    if not os.path.exists(ICON_PATH):
        print(f"Erro: icone nao encontrado em {ICON_PATH}")
        return

    _history = load_history()

    # Initial status check
    output = run_command("sudo /opt/lampp/lampp status")
    _status.update(_parse_status(output))

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

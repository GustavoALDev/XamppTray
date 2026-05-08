import subprocess


def notify(title: str, message: str) -> None:
    msg = message or "Sem resposta do comando."
    subprocess.run(["notify-send", title, msg], capture_output=True)

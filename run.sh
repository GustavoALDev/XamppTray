#!/usr/bin/env bash

# Diretorio do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Verifica se o python3-venv esta instalado (necessario para criar o venv)
if ! dpkg -l | grep -q python3-venv; then
    echo "[!] O pacote python3-venv parece nao estar instalado."
    echo "Sugestao: sudo apt install python3-venv"
fi

# Diretorio de logs
LOG_DIR="$HOME/.local/share/xampp-tray/logs"
mkdir -p "$LOG_DIR"
SETUP_LOG="$LOG_DIR/setup.log"

# Cria o ambiente virtual se nao existir
if [ ! -d "$VENV_DIR" ]; then
    echo "--- Criando ambiente virtual Python ---"
    python3 -m venv "$VENV_DIR" || { echo "Falha ao criar venv. Verifique se tem o python3-venv instalado."; exit 1; }
    echo "--- Instalando dependencias (log em $SETUP_LOG) ---"
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" > "$SETUP_LOG" 2>&1 || { echo "Falha na instalacao de dependencias. Veja $SETUP_LOG"; exit 1; }
fi

# Executa o aplicativo
echo "--- Iniciando XAMPP Tray v2.1.2 ---"
if ! "$VENV_DIR/bin/python" "$SCRIPT_DIR/main.py"; then
    echo "[!] O aplicativo encerrou com erro."
    echo "Verifique o log em: $LOG_DIR/xampp-tray.log"
fi

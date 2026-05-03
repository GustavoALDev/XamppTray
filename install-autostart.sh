#!/usr/bin/env bash
# Instala o XAMPP Tray App sem precisar do .deb:
#   - Autostart na sessao do usuario
#   - Atalho no menu de aplicativos
#   - Atalho na area de trabalho (opcional)
# Uso: bash install-autostart.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOSTART_DIR="$HOME/.config/autostart"
LOCAL_APPS_DIR="$HOME/.local/share/applications"
DESKTOP_DIR="$HOME/Desktop"
ICON="$SCRIPT_DIR/assets/xampp.png"
EXEC="python3 $SCRIPT_DIR/main.py"

DESKTOP_CONTENT="[Desktop Entry]
Type=Application
Name=XAMPP Tray
GenericName=XAMPP Control
Comment=Control XAMPP from the system tray
Exec=$EXEC
Icon=$ICON
Terminal=false
StartupNotify=false
Categories=Development;WebDevelopment;
Keywords=xampp;apache;mysql;server;php;"

# 1. Autostart
mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_DIR/xampp-tray.desktop" <<EOF
[Desktop Entry]
Type=Application
Exec=$EXEC
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=XAMPP Tray
Comment=Control XAMPP from the system tray
Icon=$ICON
Categories=Development;WebDevelopment;
EOF
echo "[OK] Autostart: $AUTOSTART_DIR/xampp-tray.desktop"

# 2. Menu de aplicativos
mkdir -p "$LOCAL_APPS_DIR"
echo "$DESKTOP_CONTENT" > "$LOCAL_APPS_DIR/xampp-tray.desktop"
echo "[OK] Menu de aplicativos: $LOCAL_APPS_DIR/xampp-tray.desktop"

# 3. Area de trabalho (cria somente se o diretorio existir)
if [ -d "$DESKTOP_DIR" ]; then
    echo "$DESKTOP_CONTENT" > "$DESKTOP_DIR/xampp-tray.desktop"
    chmod +x "$DESKTOP_DIR/xampp-tray.desktop"
    echo "[OK] Area de trabalho: $DESKTOP_DIR/xampp-tray.desktop"
else
    echo "[--] Area de trabalho nao encontrada em $DESKTOP_DIR, pulando."
fi

echo ""
echo "Pronto. O app aparecera no menu de aplicativos imediatamente."
echo "O autostart entra em vigor na proxima sessao."

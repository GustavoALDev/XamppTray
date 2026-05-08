#!/usr/bin/env bash
# Gera xampp-tray_2.1.2_amd64.deb a partir dos arquivos do projeto.
# Uso: cd packaging && bash build-deb.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PKG_DIR="$SCRIPT_DIR/deb-pkg"
OUTPUT="$PROJECT_DIR/xampp-tray_2.1.2_amd64.deb"

echo "Copiando arquivos da aplicacao..."

# Python package (src layout)
APP_SHARE="$PKG_DIR/usr/share/xampp-tray"
rm -rf "$APP_SHARE/src"
mkdir -p "$APP_SHARE/src"
cp -r "$PROJECT_DIR/src" "$APP_SHARE/"

# Legacy entry point kept for the shell wrapper
cp "$PROJECT_DIR/main.py" "$APP_SHARE/main.py"
cp "$PROJECT_DIR/requirements.txt" "$APP_SHARE/requirements.txt"

# Assets
mkdir -p "$APP_SHARE/assets/icons"
cp "$PROJECT_DIR/assets/xampp.png" "$APP_SHARE/assets/xampp.png"
for size in 16 32 48 64 128 256; do
    mkdir -p "$PKG_DIR/usr/share/icons/hicolor/${size}x${size}/apps"
    cp "$PROJECT_DIR/assets/icons/${size}x${size}.png" \
       "$PKG_DIR/usr/share/icons/hicolor/${size}x${size}/apps/xampp-tray.png"
done

# Uninstall helper
cp "$PROJECT_DIR/uninstall-clean.sh" "$APP_SHARE/uninstall-clean.sh"

# Desktop file — source of truth is the project root
mkdir -p "$PKG_DIR/usr/share/applications"
cp "$PROJECT_DIR/xampp-tray.desktop" "$PKG_DIR/usr/share/applications/xampp-tray.desktop"

echo "Embutindo dependencias Python..."
rm -rf "$APP_SHARE/lib"
mkdir -p "$APP_SHARE/lib"

SYS_PYTHON="/usr/bin/python3"
PIP_CMD="$SYS_PYTHON -m pip"

if ! $PIP_CMD --version >/dev/null 2>&1; then
    echo "[ERRO] pip nao encontrado em $SYS_PYTHON. Execute: sudo apt install python3-pip"
    exit 1
fi

# Pin versions using requirements.txt for reproducibility
$PIP_CMD install --quiet \
    --target "$APP_SHARE/lib" \
    --break-system-packages \
    -r "$PROJECT_DIR/requirements.txt" \
    || $PIP_CMD install --quiet \
        --target "$APP_SHARE/lib" \
        -r "$PROJECT_DIR/requirements.txt"

echo "Ajustando permissoes..."
chmod 755 "$PKG_DIR/DEBIAN/postinst"
chmod 755 "$PKG_DIR/DEBIAN/prerm"
chmod 755 "$PKG_DIR/DEBIAN/postrm"
chmod 755 "$PKG_DIR/usr/local/bin/xampp-tray"
chmod 755 "$APP_SHARE/uninstall-clean.sh"

echo "Construindo pacote .deb..."
dpkg-deb --build --root-owner-group "$PKG_DIR" "$OUTPUT"

echo ""
echo "Pacote gerado: $OUTPUT"
echo "Para instalar: sudo dpkg -i $OUTPUT"

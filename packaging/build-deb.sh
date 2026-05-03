#!/usr/bin/env bash
# Gera xampp-tray_1.2.3_all.deb a partir dos arquivos do projeto.
# Uso: cd packaging && bash build-deb.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PKG_DIR="$SCRIPT_DIR/deb-pkg"
OUTPUT="$PROJECT_DIR/xampp-tray_1.2.3_all.deb"

echo "Copiando arquivos da aplicacao..."
cp "$PROJECT_DIR/main.py"          "$PKG_DIR/usr/share/xampp-tray/main.py"
cp "$PROJECT_DIR/requirements.txt" "$PKG_DIR/usr/share/xampp-tray/requirements.txt"
cp "$PROJECT_DIR/assets/xampp.png" "$PKG_DIR/usr/share/xampp-tray/assets/xampp.png"
for size in 16 32 48 64 128 256; do
    mkdir -p "$PKG_DIR/usr/share/icons/hicolor/${size}x${size}/apps"
    cp "$PROJECT_DIR/assets/icons/${size}x${size}.png" "$PKG_DIR/usr/share/icons/hicolor/${size}x${size}/apps/xampp-tray.png"
done
cp "$PROJECT_DIR/uninstall-clean.sh" "$PKG_DIR/usr/share/xampp-tray/uninstall-clean.sh"

mkdir -p "$PKG_DIR/usr/share/applications"
cp "$PROJECT_DIR/xampp-tray.desktop" "$PKG_DIR/usr/share/applications/xampp-tray.desktop"

echo "Ajustando permissoes..."
chmod 755 "$PKG_DIR/DEBIAN/postinst"
chmod 755 "$PKG_DIR/DEBIAN/prerm"
chmod 755 "$PKG_DIR/DEBIAN/postrm"
chmod 755 "$PKG_DIR/usr/local/bin/xampp-tray"
chmod 755 "$PKG_DIR/usr/share/xampp-tray/uninstall-clean.sh"



echo "Construindo pacote .deb..."
dpkg-deb --build --root-owner-group "$PKG_DIR" "$OUTPUT"

echo ""
echo "Pacote gerado: $OUTPUT"
echo "Para instalar: sudo dpkg -i $OUTPUT"

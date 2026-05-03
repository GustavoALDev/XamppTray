#!/bin/bash
# Script para desinstalação completa e limpa do xampp-tray

if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute como root (use sudo)."
  exit 1
fi

echo "=== Iniciando desinstalacao limpa do xampp-tray ==="

# 1. Parar processos em execução
echo "Parando processos..."
pkill -f "/usr/share/xampp-tray/main.py" 2>/dev/null || true
pkill -f "xampp-tray" 2>/dev/null || true

# 2. Remover pacote via dpkg/apt se instalado
echo "Removendo pacote via gerenciador de pacotes..."
apt-get purge -y xampp-tray 2>/dev/null || true
dpkg -P xampp-tray 2>/dev/null || true

# 3. Forcar limpeza do banco de dados do dpkg caso esteja travado
echo "Limpando arquivos de status do dpkg..."
rm -f /var/lib/dpkg/info/xampp-tray.*

# 4. Remover arquivos do sistema
echo "Removendo arquivos instalados..."
rm -rf /usr/share/xampp-tray
rm -f /usr/share/applications/xampp-tray.desktop
rm -f /usr/local/bin/xampp-tray
rm -f /etc/sudoers.d/xampp-tray
rm -f /usr/share/metainfo/xampp-tray.metainfo.xml

# 5. Remover icones
echo "Removendo icones..."
find /usr/share/icons -name "xampp-tray.png" -delete 2>/dev/null || true
gtk-update-icon-cache /usr/share/icons/hicolor 2>/dev/null || true

# 6. Remover cache e configuracoes de todos os usuarios
echo "Removendo caches e configuracoes locais..."
for user_dir in /home/*; do
    if [ -d "$user_dir/.local/share/xampp-tray" ]; then
        echo "Limpando cache do usuario: $user_dir"
        rm -rf "$user_dir/.local/share/xampp-tray"
    fi
    rm -f "$user_dir/.local/share/applications/xampp-tray.desktop"
done
rm -rf /root/.local/share/xampp-tray

echo "=== Desinstalacao concluida com sucesso! ==="

#!/usr/bin/env bash
# Dev launcher — roda o app diretamente a partir do source sem instalar.
# Uso: bash run.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src"
exec python3 -m xampp_tray "$@"

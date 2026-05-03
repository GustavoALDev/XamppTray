# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este projeto

Aplicativo de bandeja do sistema (system tray) para Linux que permite controlar o XAMPP via menu de contexto, sem precisar abrir terminal. Escrito em Python puro, arquivo único.

## Comandos essenciais

```bash
# Instalar dependências no virtualenv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Executar o app
python3 main.py

# Instalar como autostart no GNOME
cp xampp-tray.desktop ~/.config/autostart/
```

O XAMPP precisa estar instalado em `/opt/lampp/`. Os comandos `lampp start/stop/restart/status` exigem `sudo` — o sistema precisa estar configurado com `sudoers` para permitir execução sem senha, ou o usuário será solicitado a digitar a senha via terminal.

## Arquitetura

Todo o código da aplicação está em `main.py`. O fluxo é:

1. `setup()` carrega o ícone (`assets/xampp.png`) e monta o menu via `pystray`
2. Cada item do menu chama `run_command()` que executa subprocessos do `lampp`
3. `notify()` usa `notify-send` para exibir notificações no desktop com o output dos comandos

Não há estado persistente, banco de dados, configuração externa nem módulos adicionais.

## Dependências

- `pystray` — integração com a bandeja do sistema
- `Pillow` — carregamento do ícone PNG

## Toolkit de agentes (`.agent/`)

O diretório `.agent/` contém o **Antigravity Kit** — um sistema de agentes, skills e workflows para IA. Ele **não faz parte da aplicação** e não é executado como código Python normal. É usado apenas como contexto para assistentes de IA.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este projeto

Aplicativo de bandeja do sistema (system tray) para Linux que permite controlar o XAMPP via menu de contexto, sem precisar abrir terminal. Distribuído como pacote `.deb` e executável como pacote Python instalável.

## Comandos essenciais

```bash
# Instalar em modo desenvolvimento (com deps de teste)
pip install -e ".[dev]"

# Executar o app a partir do source (sem instalar)
bash run.sh
# ou:
PYTHONPATH=src python3 -m xampp_tray

# Rodar testes
PYTHONPATH=src python3 -m pytest

# Type check
mypy src/

# Lint
ruff check src/ tests/

# Instalar autostart manualmente (source install)
bash install-autostart.sh

# Build do pacote .deb
cd packaging && bash build-deb.sh
```

O XAMPP precisa estar instalado em `/opt/lampp/`. Os comandos `lampp` exigem `sudo` — o `postinst` do .deb cria entradas no sudoers automaticamente. Em desenvolvimento, configure o sudoers manualmente ou use `pkexec`.

## Arquitetura

O código da aplicação está em `src/xampp_tray/`. Cada módulo tem responsabilidade única:

| Módulo | Responsabilidade |
|--------|-----------------|
| `app.py` | Classe `TrayApp` — orquestra todos os módulos |
| `service.py` | Classe `XamppService` — executa comandos lampp via subprocess |
| `status.py` | Classe `StatusPoller` — thread de polling com callback `on_change` |
| `config.py` | Classe `ConfigManager` — load/save de `~/.local/share/xampp-tray/config.json` |
| `history.py` | Classe `HistoryManager` — load/save do histórico de notificações |
| `icon.py` | Funções puras de geração de ícone com dots de status |
| `menu.py` | Função `build_menu()` — recebe estado explícito por parâmetro |
| `notifications.py` | Wrapper para `notify-send` |
| `constants.py` | Constantes globais e resolução de paths |
| `__main__.py` | Entry point: `python -m xampp_tray` |

`main.py` na raiz é apenas um wrapper de compatibilidade para o pacote `.deb`.

## Dependências

- `pystray` — integração com a bandeja do sistema
- `Pillow` — carregamento e manipulação do ícone PNG

## Testes

```bash
PYTHONPATH=src python3 -m pytest          # todos os testes
PYTHONPATH=src python3 -m pytest -k svc   # filtrar por nome
```

Testes não precisam de display X nem do XAMPP instalado. O `XamppService` é mockado com `unittest.mock.patch`.

## Toolkit de agentes (`.agent/`)

O diretório `.agent/` contém o **Antigravity Kit** — sistema de agentes e skills para IA. Não faz parte da aplicação e não deve ser modificado.

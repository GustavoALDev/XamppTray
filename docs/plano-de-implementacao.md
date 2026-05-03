# Plano de Implementação — XAMPP Tray App

## Contexto

O projeto é um app de bandeja do sistema (system tray) para Linux que controla o XAMPP via menu de contexto (`main.py`, Python puro). Este documento descreve as quatro melhorias planejadas, divididas em fases para execução incremental.

---

## Fase 1 — Indicadores visuais de status

**Objetivo:** mostrar no ícone da bandeja e no menu se Apache e MySQL estão rodando.

### Etapas

1. Adicionar thread de polling que executa `sudo /opt/lampp/lampp status` a cada 5 segundos
2. Parsear a saída para detectar se `apache` e `mysql` estão `running`
3. Usar Pillow `ImageDraw` para sobrepor bolinhas coloridas no ícone:
   - Verde = serviço rodando
   - Vermelho = serviço parado
4. Atualizar `icon.icon` dinamicamente no pystray
5. Adicionar itens informativos de leitura no topo do menu (`enabled=False`)

### Arquivos modificados
- `main.py`

---

## Fase 2 — Histórico de notificações em cache

**Objetivo:** manter histórico das últimas notificações com timestamp, acessível via submenu.

### Etapas

1. Criar lista global `notification_history` com entradas `{time, title, message}`
2. Modificar `notify()` para registrar cada notificação na lista (máx. 20, FIFO)
3. Persistir em `~/.local/share/xampp-tray/history.json`
4. Carregar histórico ao iniciar o app
5. Adicionar submenu "Histórico" no menu do pystray com os últimos registros

### Arquivos modificados
- `main.py`

---

## Fase 3 — Autostart com o OS

**Objetivo:** o app inicia automaticamente com a sessão no GNOME/Zorin OS.

### Etapas

1. Corrigir `xampp-tray.desktop`: substituir caminho hardcoded por `/usr/local/bin/xampp-tray`
2. Criar `install-autostart.sh` para instalação manual (sem .deb):
   - Copia o `.desktop` para `~/.config/autostart/` com o caminho correto do projeto atual

### Arquivos modificados/criados
- `xampp-tray.desktop`
- `install-autostart.sh` (novo)

---

## Fase 4 — Empacotamento como .deb

**Objetivo:** gerar `xampp-tray_1.0.0_all.deb` instalável no Zorin OS via `dpkg -i`.

### Estrutura do pacote

```
packaging/
├── build-deb.sh              # script que monta e compila o .deb
└── deb-pkg/
    ├── DEBIAN/
    │   ├── control           # metadados: nome, versão, dependências
    │   ├── postinst          # pós-instalação: instala pip deps, configura autostart
    │   └── prerm             # pré-remoção: limpa arquivos gerados
    ├── usr/
    │   ├── local/bin/
    │   │   └── xampp-tray    # wrapper script que executa main.py
    │   └── share/
    │       ├── xampp-tray/   # arquivos da aplicação
    │       │   ├── main.py
    │       │   ├── requirements.txt
    │       │   └── assets/xampp.png
    │       └── icons/hicolor/48x48/apps/
    │           └── xampp-tray.png
    └── etc/
        └── xdg/autostart/
            └── xampp-tray.desktop
```

### Etapas

1. Criar estrutura de diretórios em `packaging/`
2. Escrever `DEBIAN/control` com dependências (`python3`, `python3-pip`, `libnotify-bin`)
3. Escrever `DEBIAN/postinst` para instalar `pystray` e `Pillow` no diretório da app
4. Escrever `DEBIAN/prerm` para limpeza na desinstalação
5. Criar wrapper script `/usr/local/bin/xampp-tray`
6. Criar `build-deb.sh` que copia os arquivos e executa `dpkg-deb --build`

### Uso

```bash
cd packaging
bash build-deb.sh
sudo dpkg -i ../xampp-tray_1.0.0_all.deb
```

### Arquivos criados
- `packaging/build-deb.sh`
- `packaging/deb-pkg/DEBIAN/control`
- `packaging/deb-pkg/DEBIAN/postinst`
- `packaging/deb-pkg/DEBIAN/prerm`
- `packaging/deb-pkg/usr/local/bin/xampp-tray`

---

## Ordem de execução

| Prioridade | Fase | Impacto |
|---|---|---|
| 1 | Fase 1 — Indicadores visuais | Alto — melhora visual imediata |
| 2 | Fase 2 — Histórico de notificações | Médio — auditoria de erros |
| 3 | Fase 3 — Autostart | Médio — conveniência |
| 4 | Fase 4 — Build .deb | Alto — distribuição |

---

## Verificação por fase

- **Fase 1:** Iniciar o app, parar Apache (`sudo /opt/lampp/lampp stopapache`) e verificar se o ícone muda para vermelho em até 5s.
- **Fase 2:** Executar start/stop/status e abrir o submenu "Histórico". Reiniciar o app e confirmar que o histórico persiste.
- **Fase 3:** Copiar `.desktop` para `~/.config/autostart/`, fazer logout/login e confirmar ícone na bandeja.
- **Fase 4:** Executar `bash packaging/build-deb.sh`, instalar com `sudo dpkg -i xampp-tray_1.0.0_all.deb` e executar `xampp-tray` no terminal.

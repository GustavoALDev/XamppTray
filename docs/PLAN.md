# Plano de Ação - Integração Premium com Zorin OS

## Objetivo
Garantir que o `xampp-tray` apareça com ícone, descrição rica e notas de versão no gerenciador de programas do Zorin OS.

## Agentes Envolvidos (Orquestração)
1. **`explorer-agent`**: Mapeamento da estrutura atual (Concluído).
2. **`project-planner`**: Criação e manutenção deste plano (Atual).
3. **`devops-engineer`**: Implementação das melhorias de empacotamento e metadados.

## Alterações Propostas

### 1. Geração de Ícones
- Criar um script Python temporário para gerar múltiplos tamanhos do ícone (`16x16`, `32x32`, `64x64`, `128x128`, `256x256`) a partir do arquivo `assets/xampp.png`.
- Salvar os novos arquivos no diretório `assets/` ou diretamente na estrutura do pacote.

### 2. Metadados AppStream (`packaging/deb-pkg/usr/share/metainfo/xampp-tray.metainfo.xml`)
- Alterar a tag `<id>` para `xampp-tray.desktop` para garantir o mapeamento correto.
- Renomear o arquivo para `xampp-tray.desktop.metainfo.xml` (conforme padrão AppStream).
- **Descrição Rica**: Expandir a tag `<description>` com um texto mais profissional e chamativo.
- **Notas de Versão**: Adicionar a tag `<releases>` detalhando a versão 2.0.0:
  - Implementação de emojis de status.
  - Script de desinstalação limpa.
- **Ícone**: Ajustar a tag `<icon type="stock">xampp-tray</icon>`.

### 3. Script de Build (`packaging/build-deb.sh`)
- Atualizar o script para incluir a cópia de todos os novos tamanhos de ícone para os respectivos diretórios `usr/share/icons/hicolor/{size}/apps/xampp-tray.png`.
- Atualizar a cópia do arquivo de metainfo renomeado.

## Verificação
- Executar `build-deb.sh` para gerar o `.deb`.
- Verificar se o pacote gerado contém todos os arquivos nas pastas corretas.

# XAMPP Tray App

Interface gráfica moderna e leve para gerenciar os serviços do XAMPP (Apache e MySQL) no Linux.

## Scripts Disponíveis

Aqui está a lista de scripts disponíveis no projeto para desenvolvimento, empacotamento e gerenciamento:

### 1. Execução da Aplicação (Desenvolvimento)

Para rodar localmente com todas as dependências isoladas:

- **`run.sh`**
  - **Descrição:** Script que cria automaticamente um ambiente virtual (`venv`), instala as dependências e inicia o app.
  - **Como executar:**
    ```bash
    bash run.sh
    ```

### 2. Empacotamento

- **`packaging/build-deb.sh`**
  - **Descrição:** Gera o pacote de instalação `.deb` para distribuições baseadas em Debian/Ubuntu (como Zorin OS).
  - **Como executar:**
    ```bash
    bash packaging/build-deb.sh
    ```
  - **Resultado:** Gera o arquivo `xampp-tray_2.1.2_all.deb` no diretório raiz.

### 3. Instalação e Inicialização

- **`install-autostart.sh`**
  - **Descrição:** Configura a aplicação para iniciar automaticamente junto com o sistema operacional.
  - **Como executar:**
    ```bash
    bash install-autostart.sh
    ```

### 4. Desinstalação

- **`uninstall-clean.sh`**
  - **Descrição:** Realiza uma desinstalação limpa da aplicação, removendo arquivos residuais e configurações.
  - **Como executar:**
    ```bash
    bash uninstall-clean.sh
    ```

## Requisitos

- Python 3
- Dependências listadas em `requirements.txt` (instalar via `pip install -r requirements.txt`)
# XamppTray

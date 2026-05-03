# XAMPP Tray App

Interface gráfica moderna e leve para gerenciar os serviços do XAMPP (Apache e MySQL) no Linux.

## Scripts Disponíveis

Aqui está a lista de scripts disponíveis no projeto para desenvolvimento, empacotamento e gerenciamento:

### 1. Execução da Aplicação

- **`main.py`**
  - **Descrição:** Script principal da aplicação. Inicia a interface na bandeja do sistema.
  - **Como executar:**
    ```bash
    python3 main.py
    ```

### 2. Empacotamento

- **`packaging/build-deb.sh`**
  - **Descrição:** Gera o pacote de instalação `.deb` para distribuições baseadas em Debian/Ubuntu (como Zorin OS).
  - **Como executar:**
    ```bash
    bash packaging/build-deb.sh
    ```
  - **Resultado:** Gera o arquivo `xampp-tray_1.2.3_all.deb` no diretório raiz.

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

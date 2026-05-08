# XAMPP Tray App 🚀

![Version](https://img.shields.io/badge/version-2.1.2-blue)
![Python](https://img.shields.io/badge/python-3.x-green)
![Platform](https://img.shields.io/badge/platform-linux-orange)

[Português](#português) | [English](#english)

---

## Português

Uma interface gráfica moderna, leve e funcional para gerenciar os serviços do XAMPP (Apache e MySQL) diretamente da bandeja do sistema no Linux.

### ✨ Funcionalidades

*   🟢 **Status em Tempo Real**: Ícone dinâmico que mostra se o Apache e o MySQL estão rodando através de pontos coloridos.
*   ⚡ **Controle Rápido**: Inicie, pare ou reinicie todos os serviços com um clique.
*   ⚙️ **Configurações de Auto-start**: Opções para iniciar o app com o sistema e auto-iniciar serviços específicos.
*   📊 **Histórico**: Registro das últimas ações e notificações enviadas.
*   🔗 **Acesso Fácil**: Atalhos para o Dashboard (localhost) e para a interface gráfica oficial do XAMPP.
*   📦 **Instalação Facilitada**: Scripts para autostart e desinstalação limpa inclusos.

### 📸 Capturas de Tela

> *Em breve: Adicione suas imagens aqui para uma melhor demonstração visual.*

### 🛠️ Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/XamppTray.git
    cd XamppTray
    ```

2.  **Execute o script de inicialização:**
    O script `run.sh` criará o ambiente virtual e instalará as dependências automaticamente.
    ```bash
    bash run.sh
    ```

### 🔐 Configuração do Sudo (Opcional, mas Recomendado)

Para que o aplicativo gerencie os serviços sem solicitar senha a todo momento, você pode configurar o `sudoers`.

1.  Crie um arquivo de configuração:
    ```bash
    sudo nano /etc/sudoers.d/xampp-tray
    ```
2.  Adicione a seguinte linha (substitua `seu-usuario` pelo seu nome de usuário no Linux):
    ```text
    seu-usuario ALL=(ALL) NOPASSWD: /opt/lampp/lampp
    ```

### 📂 Scripts do Projeto

*   `run.sh`: Inicia a aplicação em ambiente isolado.
*   `install-autostart.sh`: Configura a inicialização automática com o GNOME/Desktop.
*   `packaging/build-deb.sh`: Gera um pacote `.deb` para instalação no sistema.
*   `uninstall-clean.sh`: Remove todos os arquivos e configurações do app.

---

## English

A modern, lightweight, and functional graphical interface to manage XAMPP services (Apache and MySQL) directly from the system tray on Linux.

### ✨ Features

*   🟢 **Real-time Status**: Dynamic icon showing Apache and MySQL status using colored dots.
*   ⚡ **Quick Control**: Start, stop, or restart all services with one click.
*   ⚙️ **Auto-start Settings**: Options to start the app with the system and auto-start specific services.
*   📊 **History**: Log of recent actions and sent notifications.
*   🔗 **Easy Access**: Shortcuts to Dashboard (localhost) and the official XAMPP GUI.
*   📦 **Easy Installation**: Included scripts for autostart and clean uninstallation.

### 📸 Screenshots

> *Coming soon: Add your images here for a better visual demonstration.*

### 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/XamppTray.git
    cd XamppTray
    ```

2.  **Run the startup script:**
    The `run.sh` script will automatically create a virtual environment and install dependencies.
    ```bash
    bash run.sh
    ```

### 🔐 Sudo Configuration (Optional but Recommended)

To allow the app to manage services without asking for your password every time, you can configure `sudoers`.

1.  Create a configuration file:
    ```bash
    sudo nano /etc/sudoers.d/xampp-tray
    ```
2.  Add the following line (replace `your-username` with your Linux username):
    ```text
    your-username ALL=(ALL) NOPASSWD: /opt/lampp/lampp
    ```

### 📂 Project Scripts

*   `run.sh`: Starts the application in an isolated environment.
*   `install-autostart.sh`: Configures auto-start with GNOME/Desktop.
*   `packaging/build-deb.sh`: Generates a `.deb` package for system installation.
*   `uninstall-clean.sh`: Removes all app files and configurations.

---
**Version:** 2.1.2 | **Maintainer:** GustavoALDev

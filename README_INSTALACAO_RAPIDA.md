# Guia de Instalação Rápida

Este guia contém instruções simplificadas para instalar e executar o bot rapidamente em diferentes sistemas operacionais.

## Windows

1. **Instalação com Script Automático**
   - Baixe e instale [Python 3.9+ (64-bit)](https://www.python.org/downloads/windows/) marcando "Add Python to PATH"
   - Clique duas vezes no arquivo `run_windows.bat` 
   - Siga as instruções na tela para configurar as credenciais

2. **Instalação Manual**
   - Instale Python 3.9+ e adicione ao PATH
   - Abra o Prompt de Comando como administrador
   - Execute:
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     pip install -r requirements_render.txt
     python check_environment.py
     ```
   - Crie um arquivo `.env` com suas credenciais

## macOS

1. **Instalação com Script Automático**
   - Instale Python 3.9+: `brew install python3` (com Homebrew) ou baixe do [site oficial](https://www.python.org/downloads/macos/)
   - Abra o Terminal e execute:
     ```bash
     chmod +x install.sh
     ./install.sh
     ```

2. **Instalação Manual**
   - Instale Python 3.9+
   - Abra o Terminal
   - Execute:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements_render.txt
     python check_environment.py
     ```
   - Crie um arquivo `.env` com suas credenciais

## Linux

1. **Instalação com Script Automático**
   - Instale Python 3.9+: 
     ```bash
     # Ubuntu/Debian
     sudo apt update
     sudo apt install python3 python3-pip python3-venv
     ```
   - Execute:
     ```bash
     chmod +x install.sh
     ./install.sh
     ```

2. **Instalação Manual**
   - Instale Python 3.9+
   - Execute:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements_render.txt
     python check_environment.py
     ```
   - Crie um arquivo `.env` com suas credenciais

## Execução do Bot

### Windows
- Clique duas vezes em `run_windows.bat`
- Ou execute:
  ```cmd
  venv\Scripts\activate
  python bot_completo.py
  ```

### macOS / Linux
- Execute:
  ```bash
  ./run_universal.sh
  ```
- Ou para execução em segundo plano:
  ```bash
  ./run_universal.sh --daemon
  ```

## Variáveis de Ambiente Necessárias

Crie um arquivo `.env` na pasta raiz com:

```
TELEGRAM_TOKEN=seu_token_do_bot_aqui
MERCADO_PAGO_TOKEN=seu_token_mercado_pago_aqui
ADMIN_ID=seu_id_telegram_aqui
```

## Verificação Rápida

Para verificar se o ambiente está pronto para executar o bot:

```bash
python check_environment.py
```

## Uso Rápido no Render

1. Faça fork do repositório para sua conta GitHub
2. No Render, vá para "New" > "Web Service"
3. Conecte sua conta GitHub e selecione o repositório
4. Configure as variáveis de ambiente para:
   - `TELEGRAM_TOKEN`
   - `MERCADO_PAGO_TOKEN`
   - `ADMIN_ID`
5. Use as seguintes configurações:
   - Build Command: `pip install -r requirements_render.txt`
   - Start Command: `python bot_completo.py`
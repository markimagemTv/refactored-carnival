#!/bin/bash
# Script universal para executar o bot em qualquer ambiente
# Compatível com Python 3.7+ em diferentes sistemas operacionais

# Detectar a versão do Python disponível
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Erro: Python não encontrado. Por favor, instale o Python 3.7 ou superior."
    exit 1
fi

# Verificar versão mínima do Python (3.7+)
$PYTHON_CMD -c "import sys; sys.exit(0) if sys.version_info >= (3, 7) else sys.exit(1)" || {
    echo "Erro: É necessário Python 3.7 ou superior. Versão atual:"
    $PYTHON_CMD --version
    exit 1
}

echo "Usando $(${PYTHON_CMD} --version)"

# Verificar e criar ambiente virtual se necessário
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    $PYTHON_CMD -m venv venv || {
        echo "Erro ao criar ambiente virtual. Tentando método alternativo..."
        # Fallback para versões mais antigas ou sistemas sem venv
        if command -v pip &>/dev/null; then
            pip install virtualenv
            virtualenv venv
        elif command -v pip3 &>/dev/null; then
            pip3 install virtualenv
            virtualenv venv
        else
            echo "Não foi possível criar um ambiente virtual. Continuando sem ele..."
        fi
    }
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    else
        echo "Não foi possível ativar o ambiente virtual. Continuando sem ele..."
    fi
fi

# Instalar dependências
echo "Instalando dependências..."
if [ -f "requirements_render.txt" ]; then
    pip install -r requirements_render.txt
else
    echo "Arquivo requirements_render.txt não encontrado. Instalando dependências básicas..."
    pip install python-telegram-bot==13.15 mercadopago==2.2.0 python-dotenv==1.0.0 APScheduler==3.10.1 requests==2.31.0
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Arquivo .env não encontrado. Criando a partir do exemplo..."
        cp .env.example .env
        echo "Por favor, edite o arquivo .env com suas credenciais antes de continuar."
        exit 1
    else
        echo "AVISO: Arquivo .env não encontrado. Certifique-se de que as variáveis de ambiente estão configuradas."
    fi
fi

# Criar diretório de dados se não existir
mkdir -p data

# Iniciar o bot
echo "Iniciando o bot..."
if [ "$1" == "--daemon" ]; then
    echo "Executando em modo daemon..."
    nohup $PYTHON_CMD bot_completo.py > bot.log 2>&1 &
    echo "Bot iniciado em segundo plano. Logs em bot.log"
    echo "PID: $!"
else
    $PYTHON_CMD bot_completo.py
fi
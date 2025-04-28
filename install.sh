#!/bin/bash
# Script de instalação automática para o bot

# Cores para a saída
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}=  INSTALAÇÃO AUTOMÁTICA DO BOT DE VENDAS  =${NC}"
echo -e "${BLUE}=============================================${NC}"

# Função para verificar o resultado de comandos
check_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        exit 1
    fi
}

# Verificar Python
echo -e "\n${YELLOW}Verificando instalação do Python...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    echo -e "${RED}Python não encontrado. Por favor, instale Python 3.7 ou superior.${NC}"
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_VERSION_NUM=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")

echo -e "Versão do Python: $PYTHON_VERSION"
if [ "$PYTHON_VERSION_NUM" -lt "37" ]; then
    echo -e "${RED}Este script requer Python 3.7 ou superior.${NC}"
    exit 1
fi

# Criar ambiente virtual
echo -e "\n${YELLOW}Criando ambiente virtual...${NC}"
$PYTHON_CMD -m venv venv
check_result "Ambiente virtual criado"

# Ativar ambiente virtual
echo -e "\n${YELLOW}Ativando ambiente virtual...${NC}"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo -e "${RED}Não foi possível ativar o ambiente virtual.${NC}"
    exit 1
fi
check_result "Ambiente virtual ativado"

# Instalar dependências
echo -e "\n${YELLOW}Instalando dependências...${NC}"
pip install -r requirements_render.txt
check_result "Dependências instaladas"

# Criar diretório de dados
echo -e "\n${YELLOW}Criando diretório de dados...${NC}"
mkdir -p data
check_result "Diretório de dados criado"

# Verificar existência do arquivo .env
echo -e "\n${YELLOW}Verificando arquivo .env...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Arquivo .env foi criado a partir do exemplo.${NC}"
        echo -e "${YELLOW}Por favor, edite o arquivo .env com suas credenciais.${NC}"
    else
        echo -e "${YELLOW}Criando arquivo .env...${NC}"
        cat > .env << EOF
# Configurações do bot
# Preencha as variáveis abaixo com seus dados

# Token do seu bot Telegram (obrigatório)
TELEGRAM_TOKEN=

# Token do Mercado Pago para processar pagamentos
MERCADO_PAGO_TOKEN=

# ID do administrador (seu ID no Telegram)
ADMIN_ID=
EOF
        echo -e "${YELLOW}Arquivo .env foi criado.${NC}"
        echo -e "${YELLOW}Por favor, edite o arquivo .env com suas credenciais.${NC}"
    fi
else
    echo -e "${GREEN}Arquivo .env já existe.${NC}"
fi

# Executar verificação de ambiente
echo -e "\n${YELLOW}Verificando ambiente...${NC}"
$PYTHON_CMD check_environment.py

# Instruções finais
echo -e "\n${BLUE}=============================================${NC}"
echo -e "${GREEN}Instalação concluída!${NC}"
echo -e "${BLUE}=============================================${NC}"
echo -e "\nPara executar o bot:"
echo -e "1. Edite o arquivo .env com suas credenciais"
echo -e "2. Execute: ${YELLOW}source venv/bin/activate${NC} (Linux/Mac)"
echo -e "   ou: ${YELLOW}venv\\Scripts\\activate${NC} (Windows)"
echo -e "3. Execute: ${YELLOW}python bot_completo.py${NC}"
echo -e "\nOu use o script de execução universal:"
echo -e "${YELLOW}./run_universal.sh${NC}"
echo -e "\nPara execução em segundo plano (daemon):"
echo -e "${YELLOW}./run_universal.sh --daemon${NC}"
echo -e "\n${BLUE}=============================================${NC}"
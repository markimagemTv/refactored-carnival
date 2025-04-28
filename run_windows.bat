@echo off
REM Script para executar o bot no Windows

TITLE Bot de Vendas Telegram

echo ===================================
echo = INICIALIZANDO BOT DE VENDAS     =
echo ===================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado. Por favor, instale Python 3.7 ou superior.
    pause
    exit /b 1
)

REM Verificar se ambiente virtual existe
if not exist "venv\" (
    echo Ambiente virtual nao encontrado. Criando...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate

REM Verificar se requirements estão instalados
echo Verificando dependencias...
pip install -r requirements_render.txt

REM Criar diretório de dados
if not exist "data\" (
    echo Criando diretorio de dados...
    mkdir data
)

REM Verificar arquivo .env
if not exist ".env" (
    if exist ".env.example" (
        echo Criando .env a partir do exemplo...
        copy .env.example .env
        echo [AVISO] Edite o arquivo .env com suas credenciais antes de continuar.
        notepad .env
    ) else (
        echo Criando arquivo .env padrao...
        echo # Configuracoes do bot > .env
        echo # Preencha as variaveis abaixo com seus dados >> .env
        echo. >> .env
        echo # Token do seu bot Telegram (obrigatorio) >> .env
        echo TELEGRAM_TOKEN= >> .env
        echo. >> .env
        echo # Token do Mercado Pago para processar pagamentos >> .env
        echo MERCADO_PAGO_TOKEN= >> .env
        echo. >> .env
        echo # ID do administrador (seu ID no Telegram) >> .env
        echo ADMIN_ID= >> .env
        
        echo [AVISO] Edite o arquivo .env com suas credenciais antes de continuar.
        notepad .env
    )
    echo.
    echo =============================================================
    echo = ATENCAO: Configure o arquivo .env antes de iniciar o bot! =
    echo =============================================================
    echo.
    pause
)

REM Executar verificação de ambiente
echo Executando verificacao de ambiente...
python check_environment.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] A verificacao de ambiente detectou problemas.
    echo Deseja continuar mesmo assim? (S/N)
    choice /C SN /M "Continuar?"
    if %ERRORLEVEL% EQU 2 (
        echo Operacao cancelada pelo usuario.
        pause
        exit /b 1
    )
)

REM Iniciar o bot
echo.
echo ===================================
echo = INICIANDO BOT DE VENDAS         =
echo ===================================
echo.
echo Pressione Ctrl+C para encerrar o bot
echo.

python bot_completo.py

REM Se o script chegar aqui, é porque o bot foi encerrado
echo.
echo Bot encerrado.
pause
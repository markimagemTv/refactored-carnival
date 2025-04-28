#!/bin/bash

# Script de instalação e configuração para executar o bot no Google Cloud Platform
# Este script deve ser executado como root ou com sudo

# Atualize os pacotes do sistema
apt-get update -y
apt-get upgrade -y

# Instale o Python e ferramentas necessárias
apt-get install -y python3 python3-pip python3-venv git supervisor

# Crie um diretório para o bot
mkdir -p /opt/botatualizado

# Clone o repositório (substitua com seu repositório)
git clone https://github.com/seu-usuario/botatualizado.git /opt/botatualizado

# Configure as permissões
chown -R $(whoami):$(whoami) /opt/botatualizado
chmod +x /opt/botatualizado/bot_completo.py

# Entre no diretório do bot
cd /opt/botatualizado

# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r dependencias.txt

# Crie o arquivo .env com as variáveis de ambiente (você deve editar isso manualmente)
cat > /opt/botatualizado/.env << EOF
TELEGRAM_TOKEN=seu_token_do_telegram
MERCADO_PAGO_TOKEN=seu_token_do_mercado_pago
ADMIN_ID=seu_id_do_telegram
EOF

# Configure o arquivo de serviço do Supervisor
cat > /etc/supervisor/conf.d/telegram-bot.conf << EOF
[program:telegram-bot]
command=/opt/botatualizado/venv/bin/python /opt/botatualizado/bot_completo.py
directory=/opt/botatualizado
user=$(whoami)
autostart=true
autorestart=true
startretries=10
startsecs=10
redirect_stderr=true
stdout_logfile=/var/log/telegram-bot.log
stopasgroup=true
killasgroup=true
environment=PYTHONUNBUFFERED=1
EOF

# Recarregue o supervisor e inicie o serviço
supervisorctl reread
supervisorctl update
supervisorctl start telegram-bot

echo "Bot configurado com sucesso e rodando como serviço"
echo "Para verificar o status: supervisorctl status telegram-bot"
echo "Para ver os logs: tail -f /var/log/telegram-bot.log"
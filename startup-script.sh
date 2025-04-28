#!/bin/bash

# Script de inicialização para VM do Google Cloud
# Este script é projetado para ser usado como "startup-script" ao criar uma VM

# Configurar log
exec > >(tee -a /var/log/bot-startup.log) 2>&1
echo "Iniciando script de instalação do bot às $(date)"

# Atualizar o sistema
apt-get update -y
apt-get upgrade -y

# Instalar dependências
apt-get install -y python3 python3-pip python3-venv git supervisor

# Criar diretório para o bot
mkdir -p /opt/botatualizado

# Clonar o repositório (você precisa alterar para o seu repositório)
git clone https://github.com/seu-usuario/botatualizado.git /opt/botatualizado

# Configurar as permissões
chown -R $(whoami):$(whoami) /opt/botatualizado
chmod +x /opt/botatualizado/bot_completo.py

# Configurar o ambiente Python
cd /opt/botatualizado
python3 -m venv venv
source venv/bin/activate
pip install -r dependencias.txt

# Configurar variáveis de ambiente
# IMPORTANTE: Substitua os valores abaixo pelos seus tokens reais
cat > /opt/botatualizado/.env << EOF
TELEGRAM_TOKEN=seu_token_do_telegram
MERCADO_PAGO_TOKEN=seu_token_do_mercado_pago
ADMIN_ID=seu_id_do_telegram
EOF

# Configurar o Supervisor para manter o bot rodando
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

# Recarregar o Supervisor e iniciar o bot
supervisorctl reread
supervisorctl update
supervisorctl start telegram-bot

echo "Instalação do bot concluída às $(date)"
echo "O bot está rodando e configurado para reiniciar automaticamente"
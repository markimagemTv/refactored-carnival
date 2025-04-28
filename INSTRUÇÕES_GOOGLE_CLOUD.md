# Configuração do Bot no Google Cloud Platform

Este guia explica como configurar o bot para funcionar 24/7 em uma VM do Google Cloud Platform.

## 1. Criar uma VM no Google Cloud Platform

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Vá para "Compute Engine" > "Instâncias de VM"
4. Clique em "Criar instância"
5. Configure a VM:
   - Nome: `bot-telegram`
   - Região: escolha a mais próxima à sua localização
   - Tipo de máquina: e2-micro (2 vCPU, 1GB de RAM) é suficiente para o bot
   - Sistema operacional: Debian 11 ou Ubuntu 20.04 LTS
   - Disco de inicialização: 10GB SSD
   - Permitir tráfego HTTP e HTTPS: Sim
   - Clique em "Criar"

## 2. Conectar-se à VM

1. Clique no botão "SSH" ao lado da instância criada
2. Aguarde a conexão SSH ser estabelecida

## 3. Instalar o Bot (Método Automático)

1. Faça upload do script `gcp_setup.sh` para a VM:
   - Copie o conteúdo do arquivo `gcp_setup.sh`
   - Na sessão SSH, execute:
     ```bash
     cat > gcp_setup.sh << 'EOL'
     # Cole o conteúdo do arquivo aqui
     EOL
     ```
   - Dê permissão de execução:
     ```bash
     chmod +x gcp_setup.sh
     ```

2. Execute o script de instalação:
   ```bash
   sudo ./gcp_setup.sh
   ```

3. Edite o arquivo `.env` com suas credenciais:
   ```bash
   sudo nano /opt/botatualizado/.env
   ```
   - Edite as variáveis:
     ```
     TELEGRAM_TOKEN=seu_token_do_telegram
     MERCADO_PAGO_TOKEN=seu_token_do_mercado_pago
     ADMIN_ID=seu_id_do_telegram
     ```
   - Salve o arquivo (Ctrl+O, Enter, Ctrl+X)

4. Reinicie o serviço:
   ```bash
   sudo supervisorctl restart telegram-bot
   ```

## 4. Instalar o Bot (Método Manual)

Se preferir, você pode fazer a instalação manualmente:

1. Atualize os pacotes do sistema:
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```

2. Instale os pacotes necessários:
   ```bash
   sudo apt-get install -y python3 python3-pip python3-venv git supervisor
   ```

3. Clone o repositório:
   ```bash
   sudo mkdir -p /opt/botatualizado
   sudo git clone https://github.com/seu-usuario/botatualizado.git /opt/botatualizado
   sudo chown -R $USER:$USER /opt/botatualizado
   ```

4. Configure o ambiente virtual:
   ```bash
   cd /opt/botatualizado
   python3 -m venv venv
   source venv/bin/activate
   pip install -r dependencias.txt
   ```

5. Crie o arquivo `.env`:
   ```bash
   nano .env
   ```
   - Adicione suas credenciais:
     ```
     TELEGRAM_TOKEN=seu_token_do_telegram
     MERCADO_PAGO_TOKEN=seu_token_do_mercado_pago
     ADMIN_ID=seu_id_do_telegram
     ```

6. Configure o Supervisor:
   ```bash
   sudo nano /etc/supervisor/conf.d/telegram-bot.conf
   ```
   - Adicione a configuração:
     ```
     [program:telegram-bot]
     command=/opt/botatualizado/venv/bin/python /opt/botatualizado/bot_completo.py
     directory=/opt/botatualizado
     user=seu-usuario
     autostart=true
     autorestart=true
     startretries=10
     startsecs=10
     redirect_stderr=true
     stdout_logfile=/var/log/telegram-bot.log
     stopasgroup=true
     killasgroup=true
     environment=PYTHONUNBUFFERED=1
     ```
   - Substitua `seu-usuario` pelo seu nome de usuário na VM

7. Inicie o serviço:
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start telegram-bot
   ```

## 5. Verificar Status e Logs

Para verificar se o bot está funcionando:

```bash
sudo supervisorctl status telegram-bot
```

Para ver os logs em tempo real:

```bash
sudo tail -f /var/log/telegram-bot.log
```

## 6. Configuração Alternativa com SystemD

Caso prefira usar SystemD em vez do Supervisor:

1. Crie um arquivo de serviço:
   ```bash
   sudo nano /etc/systemd/system/telegram-bot.service
   ```
   
2. Adicione o conteúdo do arquivo `systemd_service.txt`

3. Ative e inicie o serviço:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-bot
   sudo systemctl start telegram-bot
   ```

4. Verifique o status:
   ```bash
   sudo systemctl status telegram-bot
   ```

## 7. Manter o Bot Funcionando 24/7

- **Supervisor** ou **SystemD** garantirá que o bot seja reiniciado automaticamente em caso de falhas
- Configure a VM para não ser interrompida automaticamente:
  - No Console GCP, vá para "Instâncias de VM"
  - Clique em "Configurações"
  - Desative "Encerramento automático"

## 8. Monitoramento e Manutenção

1. Configure monitoramento básico:
   ```bash
   sudo apt-get install -y htop
   ```

2. Agende atualizações automáticas de segurança:
   ```bash
   sudo apt-get install -y unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

## 9. Backup dos Dados (Opcional)

Se necessário, configure backups regulares dos dados:

```bash
# Criar script de backup
sudo nano /opt/backup-bot.sh
```

Adicione:
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
sudo cp -r /opt/botatualizado/data /opt/backups/data-$DATE
```

Configure as permissões:
```bash
sudo chmod +x /opt/backup-bot.sh
```

Adicione ao crontab para execução diária:
```bash
sudo crontab -e
```

Adicione:
```
0 2 * * * /opt/backup-bot.sh
```

---

Se seguir estas instruções, seu bot estará configurado para funcionar 24/7 no Google Cloud Platform de forma robusta e resiliente a falhas.
# Instruções para Implantação no Render

O Render é uma plataforma de hospedagem em nuvem que permite implantar facilmente aplicativos web, serviços em segundo plano e muito mais. Aqui estão as instruções para implantar o bot no Render:

## Pré-requisitos

1. Conta no [Render](https://render.com/)
2. Bot criado no Telegram através do [BotFather](https://t.me/botfather) (você precisará do token do bot)
3. Conta no MercadoPago e token de acesso para integração de pagamentos

## Passos para Implantação

### 1. Registre-se no Render

Acesse [Render](https://render.com/) e crie uma conta ou faça login.

### 2. Crie um novo Web Service

1. No painel do Render, clique em "New +" e selecione "Web Service"
2. Conecte seu repositório GitHub (recomendado) ou use a opção de implantação manual
3. Se estiver usando GitHub, selecione o repositório onde o bot está hospedado

### 3. Configure o Web Service

Preencha as seguintes informações:
- **Name**: Nome do seu bot (ex: meu-telegram-bot)
- **Region**: Escolha a região mais próxima de seus usuários
- **Branch**: main (ou a branch principal do seu repositório)
- **Runtime**: Python
- **Build Command**: `pip install -r requirements_render.txt`
- **Start Command**: `python bot_completo.py`

### 4. Configure as Variáveis de Ambiente

Na seção "Environment Variables", adicione as seguintes variáveis:
- `TELEGRAM_TOKEN`: O token do seu bot do Telegram
- `MERCADO_PAGO_TOKEN`: Seu token de acesso do MercadoPago
- `ADMIN_ID`: ID do administrador do bot no Telegram

### 5. Escolha o Plano

Selecione um plano adequado às suas necessidades. Para bots com poucos usuários, o plano gratuito pode ser suficiente.

### 6. Implante o Serviço

Clique em "Create Web Service" para iniciar a implantação.

### 7. Verifique o Status

Após a implantação, verifique os logs para garantir que o bot esteja funcionando corretamente. O Render fornecerá uma URL para seu serviço, mas como este é um bot do Telegram, você não precisa acessá-la.

## Solução de Problemas

Se o bot não estiver respondendo:
1. Verifique os logs no painel do Render para identificar possíveis erros
2. Confirme se todas as variáveis de ambiente estão configuradas corretamente
3. Verifique se o token do bot do Telegram está válido 
4. Reinicie o serviço se necessário

## Manutenção

O Render reiniciará automaticamente seu serviço se ele falhar. Para atualizações de código:
1. Faça push das alterações para o repositório GitHub
2. O Render detectará as alterações e reimplantará automaticamente o serviço

## Arquivos Importantes

- `requirements_render.txt`: Lista as dependências necessárias para o bot
- `run_on_render.sh`: Script opcional para inicialização personalizada
- `render.yaml`: Configuração para implantação automatizada (Blueprint)

---

Com estas instruções, seu bot deve estar funcionando 24/7 no Render de forma confiável.
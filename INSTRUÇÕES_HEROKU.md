# Instruções para Implantação no Heroku

Este guia contém instruções para implantar o bot de vendas Telegram no Heroku e mantê-lo funcionando 24/7 sem complicações.

## Pré-requisitos

- Conta no [Heroku](https://signup.heroku.com/)
- Heroku CLI instalado (opcional, mas recomendado)
- Git instalado
- Token do seu bot Telegram (obtenha via [@BotFather](https://t.me/BotFather))
- Token do Mercado Pago 
- ID do administrador no Telegram

## Método 1: Implantação Direta (Botão)

1. Clique no botão "Deploy to Heroku" abaixo:

   [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

2. Preencha os campos obrigatórios:
   - **App name**: nome único para sua aplicação
   - **TELEGRAM_TOKEN**: token do seu bot Telegram
   - **MERCADO_PAGO_TOKEN**: token do Mercado Pago
   - **ADMIN_ID**: seu ID de usuário no Telegram
   - **HEROKU_APP_NAME**: coloque o mesmo nome que você definiu em "App name"

3. Clique em "Deploy app" e aguarde a conclusão

4. Após o deploy, configure o Heroku Scheduler:
   - No painel do Heroku, vá para a aba "Resources"
   - Clique em "Heroku Scheduler" nos add-ons
   - Adicione um novo job com o comando `./check_bot_health.sh`
   - Configure para rodar a cada 10 minutos

## Método 2: Implantação via Git/CLI

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/bot-telegram-vendas.git
   cd bot-telegram-vendas
   ```

2. Faça login no Heroku:
   ```bash
   heroku login
   ```

3. Crie um aplicativo Heroku:
   ```bash
   heroku create nome-do-seu-app
   ```

4. Configure as variáveis de ambiente:
   ```bash
   heroku config:set TELEGRAM_TOKEN=seu_token_do_bot
   heroku config:set MERCADO_PAGO_TOKEN=seu_token_mercado_pago
   heroku config:set ADMIN_ID=seu_id_telegram
   heroku config:set HEROKU_APP_NAME=nome-do-seu-app
   heroku config:set USE_HEALTH_CHECK=true
   heroku config:set TZ=America/Sao_Paulo
   ```

5. Adicione o add-on Scheduler:
   ```bash
   heroku addons:create scheduler:standard
   ```

6. Envie o código para o Heroku:
   ```bash
   git push heroku main
   ```

7. Configure o job no Scheduler:
   ```bash
   heroku addons:open scheduler
   ```
   - Adicione um novo job com o comando `./check_bot_health.sh`
   - Configure para rodar a cada 10 minutos

8. Verifique os logs:
   ```bash
   heroku logs --tail
   ```

## Método 3: Implantação com Docker

Este método usa o `heroku.yml` para implantar o bot como um contêiner Docker:

1. Faça login no Heroku:
   ```bash
   heroku login
   ```

2. Crie um aplicativo Heroku:
   ```bash
   heroku create nome-do-seu-app
   ```

3. Configure o stack do Heroku para contêineres:
   ```bash
   heroku stack:set container
   ```

4. Configure as variáveis de ambiente:
   ```bash
   heroku config:set TELEGRAM_TOKEN=seu_token_do_bot
   heroku config:set MERCADO_PAGO_TOKEN=seu_token_mercado_pago
   heroku config:set ADMIN_ID=seu_id_telegram
   heroku config:set HEROKU_APP_NAME=nome-do-seu-app
   ```

5. Implante a aplicação:
   ```bash
   git push heroku main
   ```

## Garantindo Funcionamento 24/7

Para garantir que seu bot funcione continuamente no Heroku sem entrar em modo de suspensão, as seguintes otimizações foram implementadas:

1. **Sistema Anti-Sleep**: Um sistema interno faz pings periódicos para manter a aplicação ativa.

2. **Diretório Temporário**: Os dados são armazenados no diretório `/tmp` para compatibilidade com o sistema de arquivos efêmero do Heroku.

3. **Persistência de Dados**: Um sistema de backup automático salva periodicamente os dados em arquivo.

4. **Verificações de Saúde**: O script `check_bot_health.sh` monitora a saúde do bot e o reinicia se necessário.

5. **Parâmetros Otimizados**: Timeouts e configurações de polling foram ajustados para maior estabilidade.

6. **Tratamento de Falhas**: Sistema de recuperação automática em caso de falhas transitórias.

## Verificando o Status do Bot

Para verificar se seu bot está funcionando corretamente:

1. Acesse seus logs:
   ```bash
   heroku logs --tail
   ```

2. Procure por mensagens como:
   - "Starting bot polling..."
   - "Keep-alive ping: 200"
   - "Bot está rodando normalmente" (do check_bot_health.sh)

3. Teste interagindo com seu bot no Telegram

## Solução de Problemas

Se o bot parar de funcionar:

1. **Verifique os logs**:
   ```bash
   heroku logs --tail
   ```

2. **Execute verificação de saúde manualmente**:
   ```bash
   heroku run ./check_bot_health.sh
   ```

3. **Reinicie o dyno**:
   ```bash
   heroku ps:restart
   ```

4. **Verifique as variáveis de ambiente**:
   ```bash
   heroku config
   ```

5. **Problemas com Scheduler**:
   - Verifique se o add-on Scheduler está ativo
   - Confirme se o job `./check_bot_health.sh` está configurado

## Melhorias para Alto Volume

Para bots com alto volume de mensagens, considere:

1. **Upgrade para Hobby ou Standard Dyno**:
   ```bash
   heroku ps:type hobby
   # ou
   heroku ps:type standard-1x
   ```

2. **Ativar metadados de dyno** (para melhor anti-sleep):
   ```bash
   heroku labs:enable runtime-dyno-metadata
   ```

3. **Desativar verificações de saúde** se causar sobrecarga:
   ```bash
   heroku config:set USE_HEALTH_CHECK=false
   ```

## Manutenção e Monitoramento

O sistema inclui:

1. **Auto-recuperação**: O bot se recupera automaticamente da maioria dos problemas.

2. **Logs Detalhados**: Registros de atividade e erros estão disponíveis nos logs do Heroku.

3. **Persistência de Dados**: Mesmo com reinícios do dyno, seus dados são preservados.

4. **Monitoramento Proativo**: O job do Scheduler verifica regularmente a saúde do bot.
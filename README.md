# Bot Telegram Atualizado

Bot de e-commerce para Telegram com integração ao Mercado Pago (PIX). Sistema completo para venda de produtos digitais com gestão de categorias, produtos, carrinho e pedidos.

## Características Principais

- Sistema completo de e-commerce para Telegram
- Integração com Mercado Pago (pagamentos via PIX)
- Armazenamento em memória (sem necessidade de banco de dados)
- Sistema de desconto para compras em grande quantidade
- Painel administrativo para gerenciar produtos e pedidos
- Notificações de novos pedidos para administradores

## Requisitos

- Python 3.9+
- python-telegram-bot v13.15
- mercadopago SDK
- Token do Telegram Bot
- Token de Acesso do Mercado Pago
- ID do administrador no Telegram

## Configuração

O bot utiliza as seguintes variáveis de ambiente:

- `TELEGRAM_TOKEN`: Token do seu bot do Telegram
- `MERCADO_PAGO_TOKEN`: Token de acesso do Mercado Pago
- `ADMIN_ID`: ID do chat do Telegram do administrador

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/botatualizado.git
cd botatualizado
```

2. Instale as dependências:
```bash
pip install -r dependencias.txt
```

3. Configure as variáveis de ambiente (crie um arquivo `.env`):
```
TELEGRAM_TOKEN=seu_token_do_telegram
MERCADO_PAGO_TOKEN=seu_token_do_mercado_pago
ADMIN_ID=seu_id_do_telegram
```

## Executando o Bot

Existem duas opções para executar o bot:

### 1. Versão Completa em Arquivo Único

Execute o bot consolidado em um único arquivo:

```bash
python bot_completo.py
```

ou

```bash
python executar_bot.py
```

### 2. Versão Modular

Execute o bot na versão modular:

```bash
python main.py
```

## Estrutura do Projeto

### Versão Consolidada (Um Único Arquivo)
Todo o código está disponível em um único arquivo para facilitar o gerenciamento:
- `bot_completo.py` - Arquivo único com todas as funcionalidades
- `executar_bot.py` - Script auxiliar para executar o bot

### Versão Modular
O código também está disponível em uma estrutura modular:
- `main.py` - Ponto de entrada principal
- `bot.py` - Classe principal do bot
- `config.py` - Configurações do bot
- `models.py` - Classes de dados
- `utils.py` - Funções utilitárias
- `handlers/` - Módulos para cada funcionalidade:
  - `registration.py` - Registro de usuários
  - `products.py` - Navegação de produtos
  - `cart.py` - Gerenciamento de carrinho
  - `payment.py` - Processamento de pagamentos
  - `orders.py` - Gerenciamento de pedidos
  - `admin.py` - Funções administrativas
  - `products_admin.py` - Gerenciamento de produtos

## Funcionalidades

### Para Usuários
- Registro com nome e telefone
- Navegação de produtos por categoria
- Adição de produtos ao carrinho
- Checkout com pagamento via PIX
- Verificação de status de pagamento
- Histórico de pedidos

### Para Administradores
- Gerenciamento de categorias e produtos
- Notificações de novos pedidos
- Marcação de pedidos como entregues ou cancelados
- Listagem de pedidos pendentes

## Comandos

- `/start` - Iniciar o bot e fazer cadastro
- `/help` - Mostrar ajuda
- `/admin` - Acessar painel administrativo (apenas admin)
- `/pending` - Listar pedidos pendentes (apenas admin)

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

MIT License
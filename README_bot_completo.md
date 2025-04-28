# Bot Telegram com MercadoPago (Versão Consolidada)

Este é um Bot de Telegram para e-commerce de produtos digitais com integração ao Mercado Pago para pagamentos via PIX.

## Características

- Sistema completo de e-commerce para Telegram
- Gerenciamento de produtos e categorias
- Integração com Mercado Pago (pagamentos via PIX)
- Armazenamento em memória (sem banco de dados)
- Sistema de desconto para compras em grande quantidade
- Painel administrativo completo para gerenciar produtos e pedidos

## Estrutura do Projeto

Todo o código foi consolidado em um único arquivo (`bot_completo.py`) para facilitar o gerenciamento e backup. Este arquivo contém:

- Classes de modelo (User, CartItem, Order, DataStore)
- Funções utilitárias
- Handlers para registro de usuários
- Handlers para navegação de produtos
- Handlers para gerenciamento de carrinho
- Handlers para pagamentos via PIX
- Handlers para administração de produtos
- Handlers para administração de pedidos

## Requisitos

- Python 3.9+
- python-telegram-bot v13.15
- mercadopago SDK
- Credenciais do Telegram Bot (TOKEN)
- Credenciais do Mercado Pago (ACCESS TOKEN)
- ID do administrador no Telegram (para funcionalidades admin)

## Variáveis de Ambiente

O bot requer as seguintes variáveis de ambiente:

- `TELEGRAM_TOKEN`: Token do seu bot do Telegram
- `MERCADO_PAGO_TOKEN`: Token de acesso do Mercado Pago
- `ADMIN_ID`: ID do chat do Telegram do administrador

## Executando o Bot

Você pode executar o bot diretamente:

```bash
python bot_completo.py
```

Ou usando o script de execução:

```bash
python executar_bot.py
```

## Funcionalidades

### Para Usuários
- Registro de usuários
- Navegação de produtos por categoria
- Adicionar produtos ao carrinho
- Checkout com pagamento via PIX
- Verificação de status de pagamento
- Histórico de pedidos

### Para Administradores
- Gerenciar categorias (adicionar, editar)
- Gerenciar produtos (adicionar, editar, excluir)
- Configurar campos necessários para produtos
- Configurar descontos para créditos
- Receber notificações de novos pedidos
- Marcar pedidos como entregues ou cancelados
- Listar pedidos pendentes

## Comandos

- `/start` - Iniciar o bot e fazer cadastro
- `/help` - Mostrar ajuda
- `/admin` - Acessar painel administrativo (apenas admin)
- `/pending` - Listar pedidos pendentes (apenas admin)

## Uso do Teclado Principal

O bot utiliza um teclado personalizado para facilitar a navegação:

- 🛍️ Produtos - Navegar pelo catálogo
- 🛒 Ver Carrinho - Ver itens no carrinho
- 📋 Meus Pedidos - Histórico de pedidos
- ❓ Ajuda - Obter ajuda

## Fluxo de Compra

1. Usuário seleciona categoria
2. Usuário seleciona produto
3. Para produtos de crédito: seleciona quantidade (desconto para 11+ unidades)
4. Para produtos de aplicativo: fornece campos necessários
5. Usuário visualiza carrinho e finaliza compra
6. Sistema gera código PIX para pagamento
7. Usuário realiza pagamento e verifica status
8. Admin recebe notificação de novo pedido pago

---

Desenvolvido com ❤️ usando python-telegram-bot e Mercado Pago SDK.
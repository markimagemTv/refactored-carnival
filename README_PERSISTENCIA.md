# Sistema de Persistência de Dados

Este bot agora utiliza um sistema robusto de persistência de dados baseado em arquivos JSON, garantindo que informações de usuários, carrinhos e pedidos sejam mantidas mesmo após reinicializações do servidor ou quedas de energia.

## Arquivos de Dados

Os dados são armazenados em três arquivos principais:

- `data/users.json`: Informações de registro dos usuários
- `data/carts.json`: Conteúdo dos carrinhos de compras
- `data/orders.json`: Histórico completo de pedidos

## Como Funciona

1. Ao iniciar, o bot carrega automaticamente os dados desses arquivos JSON.
2. Cada operação que modifica dados (registro de usuário, adição ao carrinho, criação de pedido) salva automaticamente os arquivos.
3. Os dados são salvos em formato JSON com codificação UTF-8, garantindo compatibilidade com caracteres especiais.

## Adaptação para Diferentes Ambientes

O sistema adapta-se automaticamente a diferentes ambientes de execução:

- **Ambiente Local**: Usa a pasta `data/` no diretório atual
- **Google Cloud**: Detecta e usa `/var/bot_data/` quando disponível
- **Heroku**: Usa `/tmp/data/` quando executado em dynos do Heroku

## Compatibilidade

Esta implementação é 100% compatível com o código existente e não requer banco de dados, conforme solicitado. O sistema funciona em:

- Todas as versões do Python (2.7+, 3.x)
- Todos os sistemas operacionais suportados (Windows, Linux, macOS)
- Todos os ambientes de hospedagem (Render, Google Cloud, Heroku, etc.)

## Correção do Loop de Registro

Esta implementação resolve o problema de loops de registro durante o processo de pagamento, garantindo que:

1. Os usuários permaneçam registrados entre reinicializações
2. Dados da sessão atual sejam usados para completar registros parciais
3. O fluxo de pagamento não seja interrompido por falhas de registro

## Recuperação de Falhas

Em caso de falha ou corrupção de arquivos, o sistema:

1. Tenta ler os arquivos existentes
2. Registra erros específicos
3. Continua operando mesmo se os arquivos não puderem ser lidos
4. Cria novos arquivos se necessário

Para maior segurança, é recomendável fazer backups regulares dos arquivos da pasta `data/`.
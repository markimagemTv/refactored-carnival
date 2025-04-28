# Guia de Compatibilidade e Execução

Este guia contém instruções para garantir que o bot funcione em diferentes ambientes e versões do Python, tanto em VMs locais quanto em nuvem.

## Requisitos Mínimos

- Python 3.7 ou superior (recomendado: Python 3.9+)
- pip (gerenciador de pacotes do Python)

## Dependências

As dependências do projeto estão listadas no arquivo `requirements_render.txt`:
- python-telegram-bot==13.15
- mercadopago==2.2.0
- python-dotenv==1.0.0
- APScheduler==3.10.1
- requests==2.31.0

## Ambiente Virtual (Recomendado)

Para evitar conflitos com outras versões de pacotes Python, recomenda-se usar um ambiente virtual:

### Para Python 3.9+:
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements_render.txt
```

## Variáveis de Ambiente

O bot requer as seguintes variáveis de ambiente:
- `TELEGRAM_TOKEN`: Token do seu bot do Telegram
- `MERCADO_PAGO_TOKEN`: Token de acesso do MercadoPago
- `ADMIN_ID`: ID do administrador do bot no Telegram

### Opção 1: Arquivo .env
Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
```
TELEGRAM_TOKEN=seu_token_aqui
MERCADO_PAGO_TOKEN=seu_token_mercado_pago_aqui
ADMIN_ID=seu_id_telegram_aqui
```

### Opção 2: Definir no sistema
```bash
# No Windows (PowerShell)
$env:TELEGRAM_TOKEN="seu_token_aqui"
$env:MERCADO_PAGO_TOKEN="seu_token_mercado_pago_aqui"
$env:ADMIN_ID="seu_id_telegram_aqui"

# No Linux/Mac
export TELEGRAM_TOKEN="seu_token_aqui"
export MERCADO_PAGO_TOKEN="seu_token_mercado_pago_aqui"
export ADMIN_ID="seu_id_telegram_aqui"
```

## Executando o Bot

### Método Padrão
```bash
python bot_completo.py
```

### Para Execução Persistente em VMs Linux
```bash
nohup python bot_completo.py > bot.log 2>&1 &
```

### Com Script Automático
```bash
chmod +x run_on_render.sh
./run_on_render.sh
```

## Compatibilidade entre Versões do Python

### Para Python 3.7 (se necessário)
Se você estiver usando Python 3.7, talvez seja necessário ajustar algumas funcionalidades:

1. Substituir o uso de `functools.cached_property` (introduzido no Python 3.8) por alternativas.
2. Evitar o uso de expressões de atribuição (operador walrus `:=`) introduzido no Python 3.8.

### Para PyPy ou Implementações Alternativas
O código deve funcionar em implementações alternativas do Python como PyPy, mas para garantir a compatibilidade:

1. Evite usar recursos de extensões C específicas.
2. Use `io.open()` em vez de somente `open()` para maior compatibilidade entre versões.

## Monitoramento e Recuperação Automática

Para garantir que o bot permaneça em execução:

### Usando Systemd (Linux)
Crie um serviço systemd para monitorar e reiniciar automaticamente o bot em caso de falhas. Um exemplo de configuração está disponível em `systemd_service.txt`.

### Usando Supervisord (Multiplataforma)
O Supervisord é uma ferramenta que monitora e reinicia automaticamente processos. Exemplo de configuração:

```ini
[program:telegrambot]
command=python /caminho/para/bot_completo.py
directory=/caminho/para/diretorio
autostart=true
autorestart=true
stderr_logfile=/caminho/para/logs/bot.err.log
stdout_logfile=/caminho/para/logs/bot.out.log
```

## Solução de Problemas de Compatibilidade

### Problemas com SSL em Versões Antigas do Python
Para Python 3.7 em sistemas antigos, você pode encontrar problemas de SSL. Solução:
```bash
pip install pyOpenSSL cryptography idna certifi
```

### Problemas com a Biblioteca python-telegram-bot
A versão 13.15 é a última versão compatível com a arquitetura do bot. Versões mais recentes (14+) exigiriam mudanças significativas no código.

### Erros de Codificação de Caracteres
Em sistemas Windows, você pode encontrar problemas com a codificação de caracteres. Adicione o seguinte código no início de `bot_completo.py`:
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
```

## Otimização para Ambientes com Recursos Limitados

Para VMs com poucos recursos:

1. Reduza a frequência das pesquisas (polling) do Telegram ajustando o parâmetro `timeout` em `updater.start_polling()`.
2. Desative recursos não essenciais como o APScheduler se não estiverem em uso.
3. Use um método de armazenamento mais eficiente, como SQLite em vez de armazenamento em memória para dados persistentes.

---

Seguindo estas diretrizes, o bot deve funcionar consistentemente em diferentes ambientes e versões do Python.
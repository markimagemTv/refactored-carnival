# Bot de Vendas Telegram - Guia de Compatibilidade

Este guia fornece instruções detalhadas para garantir que o bot funcione em diferentes sistemas operacionais e ambientes.

## Requisitos do Sistema

- **Python**: 3.7 ou superior (recomendado Python 3.9+)
- **Sistema Operacional**: Windows, macOS, Linux (qualquer distribuição)
- **Memória**: Mínimo 512MB RAM
- **Espaço em Disco**: 100MB disponíveis

## Verificação Rápida de Ambiente

Execute o script de verificação para confirmar se seu ambiente está configurado corretamente:

```bash
python check_environment.py
```

Este script verifica:
- Versão do Python
- Dependências instaladas
- Variáveis de ambiente
- Conexão com a API do Telegram
- Permissões de diretório de dados

## Configuração em Diferentes Sistemas Operacionais

### Windows

1. Instale o Python 3.7 ou superior do [site oficial](https://www.python.org/downloads/windows/)
2. Durante a instalação, marque a opção "Add Python to PATH"
3. Execute o script de instalação automática:
   ```
   run_windows.bat
   ```
4. O script criará um ambiente virtual, instalará as dependências e solicitará as configurações necessárias
5. Para executar o bot posteriormente, basta executar `run_windows.bat` novamente

### macOS

1. Instale o Python 3.7 ou superior:
   - Via [site oficial](https://www.python.org/downloads/macos/)
   - Ou via Homebrew: `brew install python3`
2. Abra o Terminal e execute:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. Siga as instruções na tela para configurar o bot
4. Para executar o bot posteriormente:
   ```bash
   ./run_universal.sh
   ```

### Linux

1. Instale o Python 3.7 ou superior:
   - Debian/Ubuntu: `sudo apt install python3 python3-pip python3-venv`
   - Fedora: `sudo dnf install python3 python3-pip`
   - Arch: `sudo pacman -S python python-pip`
2. Torne os scripts executáveis:
   ```bash
   chmod +x install.sh run_universal.sh check_environment.py
   ```
3. Execute o script de instalação:
   ```bash
   ./install.sh
   ```
4. Para executar o bot:
   ```bash
   ./run_universal.sh
   ```
   
### Execução em Segundo Plano (Daemon)

Para manter o bot em execução mesmo após fechar o terminal:

```bash
./run_universal.sh --daemon
```

## Solução de Problemas Comuns

### Erro de Codificação

Se encontrar erros relacionados a caracteres especiais:

1. Verifique a codificação do seu terminal
2. No Windows, execute antes de iniciar o bot:
   ```cmd
   chcp 65001
   ```
3. Certifique-se de que os arquivos estão salvos em UTF-8

### Erro na API do Telegram

Se o bot não conseguir se conectar à API do Telegram:

1. Verifique sua conexão com a internet
2. Confirme se o token do bot está correto no arquivo `.env`
3. Se estiver em um país com restrições à API do Telegram, considere usar uma VPN

### Erro ao Instalar Dependências

Se houver falha ao instalar os pacotes:

1. Atualize pip:
   ```bash
   pip install --upgrade pip
   ```
2. Em sistemas mais antigos, pode ser necessário instalar pacotes adicionais:
   ```bash
   pip install pyOpenSSL cryptography idna certifi
   ```

### Problemas com Versões Antigas do Python

Para Python 3.7 (mínimo suportado):

1. Se encontrar erros com `cached_property`, edite `bot_completo.py` e substitua:
   ```python
   # Substituir
   @functools.cached_property
   # Por
   @property
   ```

2. Se encontrar erros com expressões de atribuição (`:=`), edite o código para usar atribuições regulares.

## Uso de Proxy

Para usar o bot através de um proxy:

1. Adicione as configurações de proxy no arquivo `.env`:
   ```
   HTTP_PROXY=http://usuário:senha@proxy:porta
   HTTPS_PROXY=http://usuário:senha@proxy:porta
   ```

2. Se necessário, adicione estas linhas no início de `bot_completo.py`:
   ```python
   import os
   os.environ['HTTP_PROXY'] = 'http://usuário:senha@proxy:porta'
   os.environ['HTTPS_PROXY'] = 'http://usuário:senha@proxy:porta'
   ```

## Ambientes com Recursos Limitados

Para VMs ou dispositivos com recursos limitados:

1. Modifique os parâmetros de polling no arquivo `bot_completo.py`:
   ```python
   # Reduza a frequência de polling para economizar recursos
   updater.start_polling(timeout=60, drop_pending_updates=True)
   ```

2. Desative o APScheduler se não estiver em uso, removendo ou comentando:
   ```python
   # from apscheduler.schedulers.background import BackgroundScheduler
   # scheduler = BackgroundScheduler()
   # scheduler.start()
   ```

## Ajuda e Suporte

Se encontrar problemas não cobertos neste guia:

1. Execute o script de verificação para diagnóstico:
   ```bash
   python check_environment.py
   ```

2. Verifique os logs de erro para detalhes específicos:
   ```bash
   cat bot.log  # Se estiver executando como daemon
   ```

3. Consulte a documentação oficial do python-telegram-bot em [github.com/python-telegram-bot/python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
# Instruções para Enviar o Bot para o GitHub

Siga os passos abaixo para criar um novo repositório no GitHub chamado "botatualizado" e enviar o código:

## 1. Criar um novo repositório no GitHub

1. Acesse [GitHub](https://github.com) e faça login
2. Clique no botão "+" no canto superior direito e selecione "New repository"
3. Preencha os campos:
   - Nome do repositório: `botatualizado`
   - Descrição: `Bot de e-commerce para Telegram com integração ao Mercado Pago (PIX)`
   - Visibilidade: Público (ou Privado, se preferir)
   - Inicializar com README: **NÃO** marque esta opção
   - Adicionar .gitignore: **NÃO** marque esta opção
   - Escolher licença: **NÃO** marque esta opção
4. Clique em "Create repository"

## 2. Configurar o repositório local e enviar para o GitHub

Após criar o repositório, copie e cole os seguintes comandos no terminal:

```bash
# Se você não configurou seu Git ainda, execute:
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"

# Adicione o URL remoto do seu repositório no GitHub
git remote add origin https://github.com/seu-usuario/botatualizado.git

# Envie o código para o GitHub
git commit -m "Versão inicial do bot completo"
git branch -M main
git push -u origin main
```

Substitua `seu-usuario` pelo seu nome de usuário do GitHub.

## 3. Verificar se tudo foi enviado corretamente

Acesse seu repositório no GitHub através do link:
```
https://github.com/seu-usuario/botatualizado
```

Verifique se todos os arquivos estão lá. Você deve ver:
- bot_completo.py (arquivo principal)
- executar_bot.py
- README.md 
- README_bot_completo.md
- Outros arquivos de configuração

## 4. Clonar o repositório para usar em outro lugar

Para usar este bot em outro computador ou servidor, você pode cloná-lo com:

```bash
git clone https://github.com/seu-usuario/botatualizado.git
cd botatualizado
pip install -r dependencias.txt
```

Não esqueça de criar o arquivo `.env` com suas credenciais antes de executar o bot:

```
TELEGRAM_TOKEN=seu_token_do_telegram
MERCADO_PAGO_TOKEN=seu_token_do_mercado_pago
ADMIN_ID=seu_id_do_telegram
```

## Observações Importantes

- **Nunca compartilhe** seus tokens ou credenciais no GitHub
- O arquivo `.env` está no `.gitignore` para evitar que suas credenciais sejam enviadas para o GitHub
- Use o arquivo `.env.example` como modelo para criar seu próprio arquivo `.env`
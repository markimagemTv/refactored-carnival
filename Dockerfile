FROM python:3.9-slim

# Configurar variáveis
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=America/Sao_Paulo

# Configurar fuso horário
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Instalar dependências básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório da aplicação
WORKDIR /app

# Copiar arquivos de requisitos
COPY requirements_render.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements_render.txt

# Copiar o código da aplicação
COPY . .

# Tornar scripts executáveis
RUN chmod +x run_heroku.sh check_bot_health.sh

# Iniciar o bot
CMD ["bash", "run_heroku.sh"]
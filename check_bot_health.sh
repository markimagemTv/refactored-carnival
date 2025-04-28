#!/bin/bash
# Script para verificar a saúde do bot e reiniciá-lo se necessário
# Este script pode ser usado pelo Heroku Scheduler para verificações regulares

# Configurações
MAX_RESTART_ATTEMPTS=3
LOG_FILE="/tmp/bot_health_check.log"
RESTART_COOLDOWN=300  # 5 minutos entre tentativas de reinício
PROCESS_NAME="python bot_completo.py"

# Função para logging
log() {
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> "$LOG_FILE"
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1"
}

# Verifica se estamos no Heroku
if [ -z "$DYNO" ]; then
  log "Este script é destinado para uso no Heroku"
  exit 1
fi

# Função para verificar se o bot está rodando
check_bot_process() {
  # Procura pelo processo do bot
  if ps aux | grep -v grep | grep -q "$PROCESS_NAME"; then
    log "Bot está rodando normalmente"
    return 0
  else
    log "Processo do bot não encontrado"
    return 1
  fi
}

# Função para verificar API do Telegram
check_telegram_api() {
  # Verifica se temos o token
  if [ -z "$TELEGRAM_TOKEN" ]; then
    log "ERRO: TELEGRAM_TOKEN não definido"
    return 1
  fi
  
  # Tenta fazer uma chamada simples para API do Telegram
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://api.telegram.org/bot$TELEGRAM_TOKEN/getMe")
  
  if [ "$HTTP_STATUS" -eq 200 ]; then
    log "API do Telegram está acessível"
    return 0
  else
    log "ERRO: API do Telegram não está respondendo (HTTP $HTTP_STATUS)"
    return 1
  fi
}

# Função para reiniciar o bot
restart_bot() {
  log "Tentando reiniciar o bot..."
  
  # Mata qualquer instância existente
  pkill -f "$PROCESS_NAME" || true
  sleep 5
  
  # Inicia o bot novamente
  python bot_completo.py &
  
  # Verifica se o processo iniciou
  sleep 10
  if check_bot_process; then
    log "Bot reiniciado com sucesso"
    return 0
  else
    log "ERRO: Falha ao reiniciar o bot"
    return 1
  fi
}

# Verifica se o arquivo de controle de reinícios existe
COUNT_FILE="/tmp/bot_restart_count"
LAST_RESTART_FILE="/tmp/bot_last_restart"

# Inicializa contador se não existir
if [ ! -f "$COUNT_FILE" ]; then
  echo "0" > "$COUNT_FILE"
fi

# Função para obter contador atual
get_restart_count() {
  cat "$COUNT_FILE"
}

# Função para incrementar contador
increment_restart_count() {
  count=$(get_restart_count)
  echo $((count + 1)) > "$COUNT_FILE"
  # Atualiza timestamp do último reinício
  date +%s > "$LAST_RESTART_FILE"
}

# Função para resetar contador
reset_restart_count() {
  echo "0" > "$COUNT_FILE"
}

# Verifica se passou tempo suficiente desde o último reinício
can_restart() {
  if [ ! -f "$LAST_RESTART_FILE" ]; then
    return 0
  fi
  
  last_restart=$(cat "$LAST_RESTART_FILE")
  now=$(date +%s)
  elapsed=$((now - last_restart))
  
  if [ "$elapsed" -gt "$RESTART_COOLDOWN" ]; then
    return 0
  else
    log "Muito cedo para reiniciar. Último reinício há $elapsed segundos."
    return 1
  fi
}

# Verificação principal
log "Iniciando verificação de saúde do bot..."

# Verifica se o bot está rodando
if ! check_bot_process; then
  # Verifica API do Telegram
  check_telegram_api
  
  # Decide se pode reiniciar
  restart_count=$(get_restart_count)
  
  if [ "$restart_count" -lt "$MAX_RESTART_ATTEMPTS" ] && can_restart; then
    log "Tentativa de reinício $((restart_count + 1)) de $MAX_RESTART_ATTEMPTS"
    
    # Reinicia o bot
    if restart_bot; then
      increment_restart_count
    else
      # Se falhou, também incrementa para limitar tentativas
      increment_restart_count
      log "ERRO: Reinício falhou. Tentaremos novamente mais tarde."
    fi
  elif [ "$restart_count" -ge "$MAX_RESTART_ATTEMPTS" ]; then
    log "ERRO: Número máximo de tentativas de reinício atingido ($MAX_RESTART_ATTEMPTS)"
    log "Aguardando intervenção manual ou redeploy"
  fi
else
  # Bot está rodando, verifica API
  if check_telegram_api; then
    # Tudo OK, reinicializa contador se tiver passado tempo suficiente
    if [ -f "$LAST_RESTART_FILE" ]; then
      last_restart=$(cat "$LAST_RESTART_FILE")
      now=$(date +%s)
      elapsed=$((now - last_restart))
      
      # Se estiver estável por mais de 1 hora, reseta contador
      if [ "$elapsed" -gt 3600 ]; then
        reset_restart_count
        log "Bot estável por mais de 1 hora, resetando contador de reinícios"
      fi
    fi
  fi
fi

log "Verificação de saúde concluída"
exit 0
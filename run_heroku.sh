#!/bin/bash
# Script para inicializar e executar a aplicação no ambiente Heroku

# Determinar diretório atual
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Função para logging
log() {
  echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1"
}

# Verifica se estamos no ambiente Heroku
if [ -n "$DYNO" ]; then
    log "Executando no ambiente Heroku..."
    
    # Cria diretório temporário para dados
    mkdir -p /tmp/data
    log "Diretório de dados temporário criado"
    
    # Executa script de inicialização
    log "Executando inicialização do Heroku..."
    python initialize_heroku.py
    
    # Verifica resultado da inicialização
    if [ $? -ne 0 ]; then
        log "AVISO: Inicialização com warnings, prosseguindo mesmo assim"
    else
        log "Inicialização concluída com sucesso"
    fi
    
    # Determina modo de execução
    USE_HEALTH_CHECK="${USE_HEALTH_CHECK:-true}"
    
    if [ "$USE_HEALTH_CHECK" = "true" ]; then
        # Executa o bot com monitoramento de saúde
        log "Iniciando bot com monitoramento de saúde..."
        chmod +x check_bot_health.sh
        
        # Executa verificação inicial de saúde
        ./check_bot_health.sh
        
        # Inicia o bot com tratamento de falhas
        log "Iniciando bot_completo.py com monitoramento..."
        exec python health_check.py
    else
        # Executa o bot diretamente
        log "Iniciando bot_completo.py em modo direto..."
        exec python bot_completo.py
    fi
else
    log "Este script é destinado para execução no ambiente Heroku"
    log "Para executar localmente, use run_universal.sh"
    exit 1
fi
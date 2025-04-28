#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para inicialização e configuração da aplicação no Heroku
Este script verifica e configura variáveis de ambiente e dependências para o Heroku
"""

import os
import sys
import logging
import subprocess
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('heroku_init')

def check_environment():
    """Verifica e valida as variáveis de ambiente necessárias no Heroku"""
    required_vars = ["TELEGRAM_TOKEN", "MERCADO_PAGO_TOKEN", "ADMIN_ID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        return False
    return True

def setup_dyno_metadata():
    """Configura a URL da aplicação para uso no sistema anti-sleep"""
    # No Heroku, podemos usar a variável HEROKU_APP_NAME (se definida)
    app_name = os.environ.get('HEROKU_APP_NAME')
    
    if app_name:
        heroku_url = f"https://{app_name}.herokuapp.com"
        os.environ['HEROKU_URL'] = heroku_url
        logger.info(f"URL configurada: {heroku_url}")
        return True
    else:
        logger.warning("HEROKU_APP_NAME não definida. Keep-alive pode não funcionar.")
        return False

def setup_data_directory():
    """Configura diretório de dados temporário para o Heroku"""
    if os.environ.get('DYNO'):
        data_dir = "/tmp/data"
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
                logger.info(f"Diretório de dados criado: {data_dir}")
            except Exception as e:
                logger.error(f"Erro ao criar diretório de dados: {e}")
                return False
    return True

def main():
    """Função principal de inicialização"""
    logger.info("Iniciando configuração para Heroku...")
    
    # Carrega variáveis de ambiente (se houver um arquivo .env)
    load_dotenv()
    
    # Verifica ambiente
    env_ok = check_environment()
    if not env_ok:
        logger.warning("Configuração de ambiente incompleta")
    
    # Configura metadados do Dyno
    setup_dyno_metadata()
    
    # Configura diretório de dados
    setup_data_directory()
    
    logger.info("Configuração para Heroku concluída")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
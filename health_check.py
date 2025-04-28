#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de verificação de saúde para o bot Telegram no Heroku.
Este script verifica se o bot está rodando corretamente e reinicia em caso de falha.
"""

import os
import sys
import time
import logging
import subprocess
import requests
import signal
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('health_check')

class BotHealthChecker:
    """Classe para verificar e garantir a saúde do bot no Heroku."""
    
    def __init__(self, check_interval=300):
        """Inicializa o verificador de saúde.
        
        Args:
            check_interval (int): Intervalo em segundos entre verificações
        """
        self.check_interval = check_interval
        self.token = os.environ.get('TELEGRAM_TOKEN')
        self.bot_process = None
        self.last_restart = None
        self.restart_count = 0
        self.max_restarts = 5  # Máximo de reinícios antes de desistir
        
        # Status inicial
        self.is_heroku = bool(os.environ.get('DYNO'))
        
        if self.is_heroku:
            logger.info("Executando no ambiente Heroku")
        else:
            logger.info("Executando em ambiente local")
    
    def check_telegram_api(self):
        """Verifica se a API do Telegram está acessível."""
        if not self.token:
            logger.error("TELEGRAM_TOKEN não encontrado no ambiente")
            return False
        
        try:
            # Endpoint de verificação do Telegram
            url = f"https://api.telegram.org/bot{self.token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    logger.info(f"API do Telegram OK: @{bot_info['result']['username']}")
                    return True
                else:
                    logger.warning(f"Resposta da API do Telegram não está OK: {bot_info}")
            else:
                logger.error(f"Falha ao acessar API do Telegram: HTTP {response.status_code}")
            
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar API do Telegram: {e}")
            return False
    
    def check_bot_process(self):
        """Verifica se o processo do bot está rodando."""
        if not self.bot_process:
            logger.warning("Processo do bot não está sendo monitorado")
            return False
        
        # Verifica se o processo ainda está rodando
        if self.bot_process.poll() is None:
            logger.info("Processo do bot está rodando (PID: %d)", self.bot_process.pid)
            return True
        else:
            logger.warning("Processo do bot não está rodando (código de saída: %d)", 
                        self.bot_process.returncode)
            return False
    
    def start_bot(self):
        """Inicia o processo do bot."""
        try:
            # Encerra processo anterior, se existir
            if self.bot_process and self.bot_process.poll() is None:
                logger.info("Encerrando processo anterior (PID: %d)", self.bot_process.pid)
                os.kill(self.bot_process.pid, signal.SIGTERM)
                time.sleep(5)  # Espera o processo terminar
            
            # Inicia o bot com o script principal
            logger.info("Iniciando processo do bot...")
            self.bot_process = subprocess.Popen([sys.executable, "bot_completo.py"])
            self.last_restart = datetime.now()
            self.restart_count += 1
            
            logger.info("Bot iniciado (PID: %d)", self.bot_process.pid)
            return True
        except Exception as e:
            logger.error(f"Erro ao iniciar o bot: {e}")
            return False
    
    def run_check_loop(self):
        """Executa o loop principal de verificação de saúde."""
        logger.info("Iniciando monitoramento de saúde do bot...")
        
        # Verifica API do Telegram
        if not self.check_telegram_api():
            logger.error("Falha na verificação da API do Telegram")
            return False
        
        # Inicia o bot pela primeira vez, se ainda não estiver rodando
        if not self.check_bot_process():
            logger.info("Iniciando o bot pela primeira vez...")
            if not self.start_bot():
                logger.error("Falha ao iniciar o bot")
                return False
        
        try:
            # Loop principal de verificação
            while True:
                # Pausa entre verificações
                time.sleep(self.check_interval)
                
                # Verifica status do processo
                bot_running = self.check_bot_process()
                api_accessible = self.check_telegram_api()
                
                # Decide se precisa reiniciar
                if not bot_running or not api_accessible:
                    if self.restart_count >= self.max_restarts:
                        logger.error(f"Número máximo de reinícios atingido ({self.max_restarts})")
                        return False
                    
                    logger.warning("Problema detectado, reiniciando o bot...")
                    self.start_bot()
                else:
                    # Reset contador de reinícios se estável por mais de 1 hora
                    if (self.last_restart and 
                        (datetime.now() - self.last_restart).total_seconds() > 3600):
                        self.restart_count = 0
                        logger.info("Bot estável por mais de 1 hora, resetando contador de reinícios")
        
        except KeyboardInterrupt:
            logger.info("Monitoramento interrompido pelo usuário")
        finally:
            # Encerra processo do bot no final
            if self.bot_process and self.bot_process.poll() is None:
                logger.info("Encerrando processo do bot (PID: %d)", self.bot_process.pid)
                self.bot_process.terminate()
        
        return True

def main():
    """Função principal"""
    # Verifica se deve iniciar o verificador de saúde ou apenas o bot
    use_health_check = os.environ.get('USE_HEALTH_CHECK', 'true').lower() == 'true'
    
    if use_health_check:
        checker = BotHealthChecker()
        return checker.run_check_loop()
    else:
        # Se não usar health check, apenas executa o bot diretamente
        logger.info("Verificação de saúde desativada, executando bot diretamente")
        try:
            subprocess.run([sys.executable, "bot_completo.py"])
            return True
        except Exception as e:
            logger.error(f"Erro ao executar o bot: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
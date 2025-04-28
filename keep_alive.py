"""
Script para manter a aplicação Heroku ativa (anti-idle).
Este script é usado para evitar que a aplicação entre em modo sleep no Heroku.
"""

import os
import time
import logging
import requests
import threading

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('keep_alive')

class KeepAlive:
    """Classe para manter a aplicação do Heroku ativa."""
    
    def __init__(self, interval=1200):
        """Inicializa o keep-alive.
        
        Args:
            interval (int): Intervalo em segundos entre pings (padrão: 1200 = 20 minutos)
        """
        self.interval = interval
        self.app_url = os.environ.get('HEROKU_URL')
        self.running = False
        self.thread = None
    
    def start(self):
        """Inicia o keep-alive em uma thread separada."""
        if not self.app_url:
            logger.warning("HEROKU_URL não definida. Keep-alive não será iniciado.")
            return False
        
        if self.running:
            logger.info("Keep-alive já está em execução.")
            return True
        
        self.running = True
        self.thread = threading.Thread(target=self._keep_alive_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Keep-alive iniciado para {self.app_url} (intervalo: {self.interval}s)")
        return True
    
    def stop(self):
        """Interrompe o keep-alive."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        logger.info("Keep-alive interrompido.")
    
    def _keep_alive_loop(self):
        """Loop principal que envia pings periódicos."""
        while self.running:
            try:
                response = requests.get(self.app_url, timeout=10)
                logger.info(f"Keep-alive ping: {response.status_code}")
            except Exception as e:
                logger.error(f"Erro ao fazer keep-alive ping: {e}")
            
            # Aguarda o intervalo definido
            for _ in range(int(self.interval / 10)):
                if not self.running:
                    break
                time.sleep(10)

# Uso simples como script independente
if __name__ == "__main__":
    keep_alive = KeepAlive()
    keep_alive.start()
    
    try:
        # Mantém o script rodando
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        keep_alive.stop()
        print("Keep-alive finalizado.")
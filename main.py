import logging
import os
import sys
import threading
from app import app  # Importação do Flask app necessária para o workflow "Start application"

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the bot"""
    try:
        # Execute o bot completo em vez do bot original
        logger.info("Iniciando bot_completo.py...")
        from bot_completo import main as bot_main
        bot_main()
    except Exception as e:
        logger.error(f"Erro ao iniciar bot_completo.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para gerenciamento de dados persistentes.
Este módulo fornece funções para salvar e carregar dados de usuários,
carrinhos e pedidos, garantindo persistência entre reinícios do bot.
"""

import os
import json
import logging
import threading
import time
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('data_manager')

# Determina o diretório de dados baseado no ambiente
def get_data_dir():
    # Heroku ou outro ambiente com variável DYNO
    if os.environ.get('DYNO'):
        data_dir = "/tmp/data"
    # Google Cloud ou outro ambiente
    elif os.path.exists("/var/bot_data"):
        data_dir = "/var/bot_data"
    # Diretório local padrão
    else:
        data_dir = "data"
    
    # Garante que o diretório existe
    os.makedirs(data_dir, exist_ok=True)
    logger.info(f"Usando diretório de dados: {data_dir}")
    return data_dir

class DataManager:
    """Gerencia dados persistentes do bot."""
    
    def __init__(self, auto_save=True, save_interval=300):
        """Inicializa o gerenciador de dados.
        
        Args:
            auto_save (bool): Se True, salva dados automaticamente
            save_interval (int): Intervalo em segundos para salvamento automático
        """
        self.data_dir = get_data_dir()
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.orders_file = os.path.join(self.data_dir, "orders.json")
        self.carts_file = os.path.join(self.data_dir, "carts.json")
        
        self.auto_save = auto_save
        self.save_interval = save_interval
        self.running = False
        self.save_thread = None
        
        self.users = {}
        self.orders = {}
        self.carts = {}
        
        # Tenta carregar dados existentes
        self.load_all_data()
        
        # Inicia thread de salvamento automático se necessário
        if auto_save:
            self.start_auto_save()
    
    def start_auto_save(self):
        """Inicia o salvamento automático em thread separada."""
        if self.running:
            return
        
        self.running = True
        self.save_thread = threading.Thread(target=self._auto_save_loop)
        self.save_thread.daemon = True
        self.save_thread.start()
        logger.info(f"Auto-save iniciado (intervalo: {self.save_interval}s)")
    
    def stop_auto_save(self):
        """Para o salvamento automático."""
        self.running = False
        if self.save_thread:
            self.save_thread.join(timeout=1)
        logger.info("Auto-save interrompido")
    
    def _auto_save_loop(self):
        """Loop principal de salvamento automático."""
        while self.running:
            try:
                # Salva todos os dados
                self.save_all_data()
                logger.debug("Auto-save executado com sucesso")
            except Exception as e:
                logger.error(f"Erro no auto-save: {e}")
            
            # Aguarda o próximo ciclo
            for _ in range(int(self.save_interval / 10)):
                if not self.running:
                    break
                time.sleep(10)
    
    def load_all_data(self):
        """Carrega todos os dados dos arquivos."""
        self.load_users()
        self.load_orders()
        self.load_carts()
        logger.info("Todos os dados carregados")
    
    def save_all_data(self):
        """Salva todos os dados em arquivos."""
        self.save_users()
        self.save_orders()
        self.save_carts()
    
    def load_users(self):
        """Carrega dados de usuários do arquivo."""
        if not os.path.exists(self.users_file):
            logger.info(f"Arquivo de usuários não encontrado: {self.users_file}")
            return False
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
            logger.info(f"Dados de usuários carregados: {len(self.users)} usuários")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {e}")
            return False
    
    def save_users(self):
        """Salva dados de usuários em arquivo."""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            logger.info(f"Dados de usuários salvos: {len(self.users)} usuários")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar usuários: {e}")
            return False
    
    def load_orders(self):
        """Carrega dados de pedidos do arquivo."""
        if not os.path.exists(self.orders_file):
            logger.info(f"Arquivo de pedidos não encontrado: {self.orders_file}")
            return False
        
        try:
            with open(self.orders_file, 'r', encoding='utf-8') as f:
                self.orders = json.load(f)
            logger.info(f"Dados de pedidos carregados: {len(self.orders)} pedidos")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar pedidos: {e}")
            return False
    
    def save_orders(self):
        """Salva dados de pedidos em arquivo."""
        try:
            with open(self.orders_file, 'w', encoding='utf-8') as f:
                json.dump(self.orders, f, ensure_ascii=False, indent=2)
            logger.info(f"Dados de pedidos salvos: {len(self.orders)} pedidos")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar pedidos: {e}")
            return False
    
    def load_carts(self):
        """Carrega dados de carrinhos do arquivo."""
        if not os.path.exists(self.carts_file):
            logger.info(f"Arquivo de carrinhos não encontrado: {self.carts_file}")
            return False
        
        try:
            with open(self.carts_file, 'r', encoding='utf-8') as f:
                self.carts = json.load(f)
            logger.info(f"Dados de carrinhos carregados: {len(self.carts)} carrinhos")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar carrinhos: {e}")
            return False
    
    def save_carts(self):
        """Salva dados de carrinhos em arquivo."""
        try:
            with open(self.carts_file, 'w', encoding='utf-8') as f:
                json.dump(self.carts, f, ensure_ascii=False, indent=2)
            logger.info(f"Dados de carrinhos salvos: {len(self.carts)} carrinhos")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar carrinhos: {e}")
            return False
    
    def get_user(self, user_id):
        """Obtém dados de um usuário."""
        str_id = str(user_id)  # Converte para string para garantir compatibilidade
        return self.users.get(str_id)
    
    def save_user(self, user_id, user_data):
        """Salva dados de um usuário."""
        str_id = str(user_id)  # Converte para string para garantir compatibilidade
        self.users[str_id] = user_data
        
        # Salva imediatamente se auto_save estiver desativado
        if not self.auto_save:
            self.save_users()
        
        return True
    
    def get_cart(self, user_id):
        """Obtém carrinho de um usuário."""
        str_id = str(user_id)  # Converte para string para garantir compatibilidade
        return self.carts.get(str_id, [])
    
    def update_cart(self, user_id, cart_data):
        """Atualiza carrinho de um usuário."""
        str_id = str(user_id)  # Converte para string para garantir compatibilidade
        self.carts[str_id] = cart_data
        
        # Salva imediatamente se auto_save estiver desativado
        if not self.auto_save:
            self.save_carts()
        
        return True
    
    def clear_cart(self, user_id):
        """Limpa carrinho de um usuário."""
        str_id = str(user_id)  # Converte para string para garantir compatibilidade
        self.carts[str_id] = []
        
        # Salva imediatamente se auto_save estiver desativado
        if not self.auto_save:
            self.save_carts()
        
        return True
    
    def get_order(self, order_id):
        """Obtém dados de um pedido."""
        return self.orders.get(order_id)
    
    def save_order(self, order_id, order_data):
        """Salva dados de um pedido."""
        self.orders[order_id] = order_data
        
        # Salva imediatamente se auto_save estiver desativado
        if not self.auto_save:
            self.save_orders()
        
        return True
    
    def get_user_orders(self, user_id):
        """Obtém todos os pedidos de um usuário."""
        str_id = str(user_id)  # Converte para string para garantir compatibilidade
        return [order for order_id, order in self.orders.items() 
                if order.get('user_id') == str_id]
    
    def update_order_status(self, order_id, status, payment_id=None):
        """Atualiza status de um pedido."""
        if order_id in self.orders:
            self.orders[order_id]['status'] = status
            if payment_id:
                self.orders[order_id]['payment_id'] = payment_id
            
            # Salva imediatamente se auto_save estiver desativado
            if not self.auto_save:
                self.save_orders()
            
            return True
        return False

# Cria uma instância única para uso global
data_manager = DataManager()

# Funções de conveniência
def get_user(user_id):
    return data_manager.get_user(user_id)

def save_user(user_id, user_data):
    return data_manager.save_user(user_id, user_data)

def get_cart(user_id):
    return data_manager.get_cart(user_id)

def update_cart(user_id, cart_data):
    return data_manager.update_cart(user_id, cart_data)

def clear_cart(user_id):
    return data_manager.clear_cart(user_id)

def get_order(order_id):
    return data_manager.get_order(order_id)

def save_order(order_id, order_data):
    return data_manager.save_order(order_id, order_data)

def get_user_orders(user_id):
    return data_manager.get_user_orders(user_id)

def update_order_status(order_id, status, payment_id=None):
    return data_manager.update_order_status(order_id, status, payment_id)

def save_all_data():
    return data_manager.save_all_data()

# Para uso como script independente
if __name__ == "__main__":
    dm = DataManager()
    print("Testando o gerenciador de dados...")
    
    # Exemplo: adicionar dados de teste
    dm.save_user("123456", {"name": "Usuário Teste", "phone": "987654321"})
    
    # Salvar todos os dados
    dm.save_all_data()
    
    print("Teste concluído. Verifique os arquivos no diretório de dados.")
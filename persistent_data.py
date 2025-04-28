#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para persistência de dados em memória com backup em arquivo.
Este módulo fornece funções para salvar e recuperar dados em ambientes
com sistema de arquivos efêmero, como o Heroku.
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
logger = logging.getLogger('persistent_data')

class PersistentDataManager:
    """Gerencia dados persistentes, com backup em arquivo se possível."""
    
    def __init__(self, backup_interval=300, heroku_mode=False):
        """Inicializa o gerenciador de dados persistentes.
        
        Args:
            backup_interval (int): Intervalo em segundos para salvar dados (padrão: 300s)
            heroku_mode (bool): Se True, usa o diretório temporário do Heroku
        """
        # Determinar diretório de dados baseado no ambiente
        if heroku_mode or os.environ.get('DYNO'):
            self.data_dir = "/tmp/data"
            logger.info("Usando diretório temporário Heroku: /tmp/data")
        else:
            self.data_dir = "data"
            logger.info("Usando diretório local: data")
        
        # Garantir que o diretório exista
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Erro ao criar diretório de dados: {e}")
        
        self.backup_interval = backup_interval
        self.data = {
            'users': {},
            'orders': {},
            'products': {},
            'last_backup': None
        }
        
        # Inicializa thread de backup automático
        self.running = False
        self.backup_thread = None
    
    def start_auto_backup(self):
        """Inicia o backup automático em thread separada."""
        if self.running:
            return
        
        self.running = True
        self.backup_thread = threading.Thread(target=self._backup_loop)
        self.backup_thread.daemon = True
        self.backup_thread.start()
        logger.info(f"Backup automático iniciado (intervalo: {self.backup_interval}s)")
    
    def stop_auto_backup(self):
        """Para o backup automático."""
        self.running = False
        if self.backup_thread:
            self.backup_thread.join(timeout=1)
        logger.info("Backup automático interrompido")
    
    def _backup_loop(self):
        """Loop de backup automático."""
        while self.running:
            try:
                self.save_data()
            except Exception as e:
                logger.error(f"Erro no backup automático: {e}")
            
            # Aguarda o intervalo definido
            for _ in range(int(self.backup_interval / 10)):
                if not self.running:
                    break
                time.sleep(10)
    
    def save_data(self):
        """Salva os dados em arquivo."""
        try:
            # Atualiza timestamp do último backup
            self.data['last_backup'] = datetime.now().isoformat()
            
            # Salva cada tipo de dado em um arquivo separado para evitar
            # problemas com arquivos grandes
            for data_type in ['users', 'orders', 'products']:
                filename = os.path.join(self.data_dir, f"{data_type}.json")
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.data[data_type], f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados salvos com sucesso em {self.data_dir}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
            return False
    
    def load_data(self):
        """Carrega dados dos arquivos."""
        try:
            # Carrega cada tipo de dado de seu arquivo
            for data_type in ['users', 'orders', 'products']:
                filename = os.path.join(self.data_dir, f"{data_type}.json")
                
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        self.data[data_type] = json.load(f)
            
            logger.info(f"Dados carregados com sucesso de {self.data_dir}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return False
    
    def get_data(self, data_type):
        """Recupera um tipo específico de dados."""
        return self.data.get(data_type, {})
    
    def set_data(self, data_type, new_data):
        """Define dados para um tipo específico."""
        self.data[data_type] = new_data
        return True
    
    def update_data(self, data_type, key, value):
        """Atualiza um item específico de dados."""
        if data_type not in self.data:
            self.data[data_type] = {}
        
        self.data[data_type][key] = value
        return True
    
    def delete_data(self, data_type, key):
        """Remove um item específico de dados."""
        if data_type in self.data and key in self.data[data_type]:
            del self.data[data_type][key]
            return True
        return False

# Instância global do gerenciador de dados
data_manager = PersistentDataManager()

# Funções de conveniência para uso simples
def start_backup_service():
    """Inicia o serviço de backup automático."""
    data_manager.load_data()  # Carrega dados existentes
    data_manager.start_auto_backup()
    return data_manager

def save_user(user_id, user_data):
    """Salva dados de um usuário."""
    return data_manager.update_data('users', str(user_id), user_data)

def get_user(user_id):
    """Recupera dados de um usuário."""
    users = data_manager.get_data('users')
    return users.get(str(user_id))

def save_order(order_id, order_data):
    """Salva dados de um pedido."""
    return data_manager.update_data('orders', str(order_id), order_data)

def get_order(order_id):
    """Recupera dados de um pedido."""
    orders = data_manager.get_data('orders')
    return orders.get(str(order_id))

def get_all_orders():
    """Recupera todos os pedidos."""
    return data_manager.get_data('orders')

# Teste simples
if __name__ == "__main__":
    print("Testando sistema de persistência de dados...")
    
    # Cria gerenciador com backup a cada 5 segundos (apenas para teste)
    test_manager = PersistentDataManager(backup_interval=5)
    
    # Adiciona dados de teste
    test_manager.update_data('users', '123456', {'name': 'Usuário Teste', 'phone': '123456789'})
    test_manager.update_data('orders', 'abc123', {'id': 'abc123', 'status': 'pendente'})
    
    # Inicia backup automático
    test_manager.start_auto_backup()
    
    try:
        # Aguarda 10 segundos para ver backups acontecendo
        for i in range(10):
            print(f"Aguardando... {i+1}s")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        test_manager.stop_auto_backup()
        print("Teste concluído")
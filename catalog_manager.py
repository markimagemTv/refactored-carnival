#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para gerenciamento do catálogo de produtos.
Este módulo fornece funções para exportar e importar o catálogo de produtos para JSON,
bem como integração com o sistema de versionamento Git.
"""

import json
import logging
import os
from datetime import datetime

# Configuração do logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('catalog_manager')

# Diretório padrão para armazenamento do catálogo
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def export_catalog_to_json(catalog_data, output_file='data/catalog.json'):
    """Exporta o catálogo para um arquivo JSON
    
    Args:
        catalog_data (dict): Dados do catálogo
        output_file (str): Caminho do arquivo de saída
        
    Returns:
        bool: True se a exportação foi bem-sucedida, False caso contrário
    """
    try:
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Adicionar timestamp na exportação
        if 'metadata' not in catalog_data:
            catalog_data['metadata'] = {}
        
        catalog_data['metadata']['exported_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Salvar como JSON formatado
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Catálogo exportado com sucesso para {output_file}")
        return True
    except Exception as e:
        logger.error(f"Erro ao exportar catálogo: {e}")
        return False

def import_catalog_from_json(input_file='data/catalog.json'):
    """Importa o catálogo de um arquivo JSON
    
    Args:
        input_file (str): Caminho do arquivo de entrada
        
    Returns:
        dict: Dados do catálogo ou None em caso de erro
    """
    try:
        if not os.path.exists(input_file):
            logger.warning(f"Arquivo de catálogo {input_file} não encontrado")
            return None
            
        with open(input_file, 'r', encoding='utf-8') as f:
            catalog_data = json.load(f)
            
        # Verificar se os dados têm o formato esperado
        if 'catalog' not in catalog_data:
            logger.warning("Formato de arquivo de catálogo inválido: chave 'catalog' não encontrada")
            return None
            
        logger.info(f"Catálogo importado com sucesso de {input_file}")
        return catalog_data
    except Exception as e:
        logger.error(f"Erro ao importar catálogo: {e}")
        return None

def save_catalog_to_git(catalog_data, commit_message=None):
    """Salva o catálogo e commita as mudanças para o Git
    
    Args:
        catalog_data (dict): Dados do catálogo
        commit_message (str, optional): Mensagem de commit personalizada
        
    Returns:
        bool: True se o processo foi bem-sucedido, False caso contrário
    """
    try:
        # Primeiro exporta para arquivo JSON
        if not export_catalog_to_json(catalog_data):
            logger.error("Falha ao exportar catálogo antes de commitar no Git")
            return False
            
        try:
            # Importa o módulo git_manager
            import git_manager
            
            # Verifica se está em um repositório Git
            if not git_manager.is_git_repo():
                logger.warning("Diretório atual não é um repositório Git. Apenas o arquivo local foi atualizado.")
                return False
                
            # Gerar mensagem de commit padrão se não for fornecida
            if not commit_message:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                commit_message = f"Atualização do catálogo de produtos - {timestamp}"
                
            # Commitar as mudanças usando git_manager
            success = git_manager.commit_catalog_changes(
                catalog_data, 
                commit_message=commit_message
            )
            
            if success:
                logger.info(f"Catálogo salvo e commitado com sucesso: '{commit_message}'")
            else:
                logger.warning("Falha ao commitar catálogo no Git, mas arquivo local foi atualizado")
                
            return success
        except ImportError:
            logger.warning("Módulo git_manager não disponível. Apenas a exportação local foi realizada.")
            return False
    except Exception as e:
        logger.error(f"Erro ao salvar catálogo no Git: {e}")
        return False

# Função auxiliar para teste do módulo
if __name__ == "__main__":
    test_catalog = {
        "metadata": {
            "version": "1.0",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "catalog": {
            "Categoria 1": [
                {"name": "Produto Teste 1", "price": 10.0, "discount": True},
                {"name": "Produto Teste 2", "price": 20.0, "fields": ["Campo1", "Campo2"]}
            ]
        }
    }
    
    # Teste de exportação
    export_result = export_catalog_to_json(test_catalog, "data/test_catalog.json")
    print(f"Teste de exportação: {'Sucesso' if export_result else 'Falha'}")
    
    # Teste de importação
    imported_catalog = import_catalog_from_json("data/test_catalog.json")
    print(f"Teste de importação: {'Sucesso' if imported_catalog else 'Falha'}")
    
    # Teste de salvamento no Git (requer git_manager.py)
    git_result = save_catalog_to_git(test_catalog, "Teste de commit automático")
    print(f"Teste de commit Git: {'Sucesso' if git_result else 'Falha (ou não em repositório Git)'}")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para gerenciamento de integração com Git.
Este módulo fornece funções para verificar e interagir com repositórios Git,
facilitando o versionamento automático do catálogo de produtos.
"""

import os
import subprocess
import logging
from datetime import datetime

# Configuração do logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('git_manager')

def run_git_command(command, cwd=None):
    """Executa um comando git e retorna o resultado
    
    Args:
        command (list): Lista de argumentos do comando git
        cwd (str, optional): Diretório onde executar o comando
        
    Returns:
        tuple: (success, output)
    """
    try:
        # Garantir que o comando começa com 'git'
        if not command[0].startswith('git'):
            command.insert(0, 'git')
        
        # Executar o comando
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False  # Não lançar exceção em caso de erro
        )
        
        # Verificar resultado
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            logger.warning(f"Comando git falhou: {' '.join(command)}")
            logger.warning(f"Erro: {result.stderr.strip()}")
            return False, result.stderr.strip()
    
    except Exception as e:
        logger.error(f"Erro ao executar comando git: {e}")
        return False, str(e)

def is_git_repo(path='.'):
    """Verifica se o diretório atual é um repositório Git
    
    Args:
        path (str): Caminho para verificar
        
    Returns:
        bool: True se for um repositório Git, False caso contrário
    """
    success, _ = run_git_command(['git', 'rev-parse', '--is-inside-work-tree'], cwd=path)
    return success

def get_git_status(path='.'):
    """Obtém o status do repositório Git
    
    Args:
        path (str): Caminho do repositório
        
    Returns:
        tuple: (success, output)
    """
    return run_git_command(['git', 'status', '--porcelain'], cwd=path)

def commit_catalog_changes(catalog_data, commit_message=None, path='.'):
    """Commita mudanças no catálogo de produtos para o Git
    
    Args:
        catalog_data (dict): Dados do catálogo a serem salvos
        commit_message (str, optional): Mensagem de commit personalizada
        path (str): Caminho do repositório
        
    Returns:
        bool: True se o commit foi realizado com sucesso, False caso contrário
    """
    if not is_git_repo(path):
        logger.warning("O caminho especificado não é um repositório Git válido")
        return False
    
    # Verificar se existem mudanças para commitar
    success, status_output = get_git_status(path)
    if not success:
        logger.error("Falha ao obter status do Git")
        return False
    
    # O catálogo já deve estar salvo pelo catalog_manager
    # Adicionar o arquivo ao índice do Git
    catalog_file = os.path.join('data', 'catalog.json')
    success, _ = run_git_command(['git', 'add', catalog_file], cwd=path)
    if not success:
        logger.error(f"Falha ao adicionar {catalog_file} ao índice do Git")
        return False
    
    # Verificar se há realmente mudanças para commitar
    success, status_output = get_git_status(path)
    if not success or not status_output:
        logger.info("Não há mudanças no catálogo para commitar")
        return True  # Consideramos um sucesso, não há mudanças
    
    # Definir mensagem de commit
    if not commit_message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Atualização do catálogo de produtos - {timestamp}"
    
    # Realizar o commit
    success, output = run_git_command(['git', 'commit', '-m', commit_message], cwd=path)
    if not success:
        logger.error(f"Falha ao commitar mudanças: {output}")
        return False
    
    logger.info(f"Commit realizado com sucesso: {commit_message}")
    
    # Tentar push se estiver configurado para um remote
    try:
        has_remote, _ = run_git_command(['git', 'remote'], cwd=path)
        if has_remote:
            success, push_output = run_git_command(['git', 'push'], cwd=path)
            if success:
                logger.info("Push realizado com sucesso")
            else:
                logger.warning(f"Falha ao realizar push: {push_output}")
    except Exception as e:
        logger.warning(f"Erro ao tentar realizar push: {e}")
    
    return True

def setup_git_identity(name=None, email=None, path='.'):
    """Configura a identidade Git para commits automáticos
    
    Args:
        name (str, optional): Nome do usuário Git
        email (str, optional): Email do usuário Git
        path (str): Caminho do repositório
        
    Returns:
        bool: True se a configuração foi realizada com sucesso, False caso contrário
    """
    if not is_git_repo(path):
        logger.warning("O caminho especificado não é um repositório Git válido")
        return False
    
    try:
        # Usar valores padrão se não fornecidos
        git_name = name or "Bot Telegram Automático"
        git_email = email or "bot@exemplo.com"
        
        # Configurar o nome do usuário
        success, _ = run_git_command(['git', 'config', 'user.name', git_name], cwd=path)
        if not success:
            logger.error(f"Falha ao configurar user.name para {git_name}")
            return False
        
        # Configurar o email do usuário
        success, _ = run_git_command(['git', 'config', 'user.email', git_email], cwd=path)
        if not success:
            logger.error(f"Falha ao configurar user.email para {git_email}")
            return False
        
        logger.info(f"Identidade Git configurada com sucesso: {git_name} <{git_email}>")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao configurar identidade Git: {e}")
        return False

# Função auxiliar para teste do módulo
if __name__ == "__main__":
    # Verificar se estamos em um repositório Git
    if is_git_repo():
        print("Este diretório é um repositório Git.")
        
        # Configurar identidade para testes
        if setup_git_identity("Tester", "test@example.com"):
            print("Identidade Git configurada com sucesso.")
            
        # Obter status do repositório
        success, status = get_git_status()
        if success:
            print(f"Status do repositório: {'Sem alterações' if not status else status}")
        
        # Teste de commit (requer catalog_manager para salvar o arquivo primeiro)
        try:
            import catalog_manager
            test_catalog = {
                "metadata": {
                    "version": "1.0",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "catalog": {
                    "Teste": [
                        {"name": "Produto teste do git_manager", "price": 99.99}
                    ]
                }
            }
            
            # Salvar catálogo localmente primeiro
            catalog_manager.export_catalog_to_json(test_catalog)
            
            # Tentar commitar as mudanças
            if commit_catalog_changes(test_catalog, "Teste de commit pelo git_manager.py"):
                print("Commit de teste realizado com sucesso.")
            else:
                print("Falha ao realizar commit de teste.")
        except ImportError:
            print("catalog_manager não encontrado. Teste de commit não realizado.")
    else:
        print("Este diretório não é um repositório Git.")
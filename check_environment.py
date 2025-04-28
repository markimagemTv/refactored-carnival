#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se o ambiente está configurado corretamente para executar o bot.
Ele verificará:
1. Versão do Python
2. Dependências instaladas
3. Variáveis de ambiente
4. Acesso à API do Telegram
"""

import sys
import os
import importlib
import platform

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("Verificando versão do Python...")
    version = sys.version_info
    if version < (3, 7):
        print(f"❌ Python 3.7 ou superior é necessário. Versão atual: {platform.python_version()}")
        return False
    else:
        print(f"✅ Versão do Python: {platform.python_version()}")
        return True

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("\nVerificando dependências...")
    required_packages = {
        'python-telegram-bot': 'telegram',
        'mercadopago': 'mercadopago',
        'python-dotenv': 'dotenv',
        'APScheduler': 'apscheduler',
        'requests': 'requests'
    }
    
    all_installed = True
    for package_name, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name} está instalado")
        except ImportError:
            print(f"❌ {package_name} NÃO está instalado")
            all_installed = False
    
    return all_installed

def check_environment_variables():
    """Verifica se as variáveis de ambiente necessárias estão configuradas"""
    print("\nVerificando variáveis de ambiente...")
    
    # Tentar carregar do arquivo .env se existir
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("ℹ️ Arquivo .env encontrado e carregado")
    except ImportError:
        print("ℹ️ python-dotenv não está instalado, pulando carregamento do arquivo .env")
    
    required_vars = ['TELEGRAM_TOKEN', 'MERCADO_PAGO_TOKEN', 'ADMIN_ID']
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            status = "✅ configurada"
            # Mostrar apenas os primeiros caracteres por segurança
            if var == 'TELEGRAM_TOKEN' and len(value) > 10:
                value = value[:10] + '...'
            elif var == 'MERCADO_PAGO_TOKEN' and len(value) > 10:
                value = value[:10] + '...'
        else:
            status = "❌ NÃO configurada"
            value = "ausente"
            all_set = False
        
        print(f"Variável {var}: {status} [{value}]")
    
    return all_set

def check_telegram_api():
    """Tenta se conectar à API do Telegram para verificar o token"""
    print("\nVerificando API do Telegram...")
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ Token do Telegram não configurado, pulando verificação da API")
        return False
    
    try:
        import requests
        response = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                bot_name = data['result']['username']
                print(f"✅ Conexão com API do Telegram estabelecida. Bot: @{bot_name}")
                return True
            else:
                print(f"❌ API retornou erro: {data.get('description', 'Erro desconhecido')}")
        else:
            print(f"❌ Falha na conexão com a API do Telegram. Status: {response.status_code}")
        
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar API do Telegram: {e}")
        return False

def check_data_directory():
    """Verifica se o diretório de dados existe e pode ser escrito"""
    print("\nVerificando diretório de dados...")
    data_dir = "data"
    
    # Verificar se o diretório existe
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir, exist_ok=True)
            print(f"✅ Diretório {data_dir} criado com sucesso")
        except Exception as e:
            print(f"❌ Não foi possível criar o diretório {data_dir}: {e}")
            return False
    else:
        print(f"✅ Diretório {data_dir} já existe")
    
    # Verificar permissões de escrita
    try:
        test_file = os.path.join(data_dir, "test_write.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print(f"✅ Diretório {data_dir} tem permissões de escrita")
        return True
    except Exception as e:
        print(f"❌ Não foi possível escrever no diretório {data_dir}: {e}")
        return False

def main():
    """Função principal que executa todas as verificações"""
    print("=" * 50)
    print("VERIFICAÇÃO DE AMBIENTE PARA O BOT")
    print("=" * 50)
    
    # Verificar sistema
    python_ok = check_python_version()
    deps_ok = check_dependencies()
    env_ok = check_environment_variables()
    data_ok = check_data_directory()
    api_ok = check_telegram_api()
    
    # Relatório final
    print("\n" + "=" * 50)
    print("RESUMO DA VERIFICAÇÃO")
    print("=" * 50)
    
    status_map = {True: "✅ OK", False: "❌ FALHA"}
    
    print(f"Versão do Python: {status_map[python_ok]}")
    print(f"Dependências: {status_map[deps_ok]}")
    print(f"Variáveis de ambiente: {status_map[env_ok]}")
    print(f"Diretório de dados: {status_map[data_ok]}")
    print(f"API do Telegram: {status_map[api_ok]}")
    
    # Resultado final
    all_ok = python_ok and deps_ok and env_ok and data_ok and api_ok
    
    print("\nResultado final:")
    if all_ok:
        print("✅ Ambiente PRONTO para execução do bot!")
    else:
        print("❌ Ambiente NÃO ESTÁ PRONTO. Corrija os problemas acima antes de executar o bot.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
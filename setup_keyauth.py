#!/usr/bin/env python3
"""
Script de Configuração KeyAuth para SECRIMPO
Este script ajuda você a configurar as credenciais KeyAuth com segurança
"""

import os
import json
from pathlib import Path

def setup_keyauth_credentials():
    """Configuração interativa para credenciais KeyAuth"""
    print("🔑 Configuração KeyAuth SECRIMPO")
    print("=" * 40)
    print()
    print("Você precisa obter suas credenciais KeyAuth em: https://keyauth.cc")
    print("1. Crie uma conta no KeyAuth")
    print("2. Crie uma nova aplicação")
    print("3. Obtenha seu Owner ID e Secret")
    print()
    
    # Obter credenciais
    owner_id = input("Digite seu KeyAuth Owner ID: ").strip()
    secret = input("Digite seu KeyAuth Secret: ").strip()
    app_name = input("Digite o nome da sua aplicação (padrão: SECRIMPO): ").strip() or "SECRIMPO"
    
    if not owner_id or not secret:
        print("❌ Owner ID e Secret são obrigatórios!")
        return False
    
    # Validar entradas
    print(f"\n📋 Resumo da Configuração:")
    print(f"   Nome da Aplicação: {app_name}")
    print(f"   Owner ID: {owner_id}")
    print(f"   Secret: {'*' * len(secret)} (oculto)")
    
    confirm = input("\nEstá correto? (s/N): ").strip().lower()
    
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Configuração cancelada")
        return False
    
    # Criar arquivo de ambiente
    env_file = Path(".env")
    env_content = f"""# Configuração KeyAuth para SECRIMPO
KEYAUTH_OWNER_ID={owner_id}
KEYAUTH_SECRET={secret}
KEYAUTH_APP_NAME={app_name}

# Configuração da API
API_HOST=127.0.0.1
API_PORT=8000
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ Configuração salva em {env_file}")
        
        # Atualizar configuração do backend
        config_file = Path("backend/auth/keyauth_config.py")
        if config_file.exists():
            # Ler configuração atual
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir valores placeholder
            content = content.replace('os.getenv("KEYAUTH_OWNER_ID", "YOUR_OWNER_ID")', f'os.getenv("KEYAUTH_OWNER_ID", "{owner_id}")')
            content = content.replace('os.getenv("KEYAUTH_SECRET", "YOUR_SECRET")', f'os.getenv("KEYAUTH_SECRET", "{secret}")')
            
            # Escrever de volta
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Configuração do backend atualizada")
        
        print("\n🎯 Próximos Passos:")
        print("1. Crie assinaturas no seu painel KeyAuth:")
        print("   - admin: Acesso completo")
        print("   - agent: Acesso para criar/editar")
        print("   - viewer: Acesso somente leitura")
        print("   - restricted: Acesso mínimo")
        print("2. Gere chaves de licença para seus usuários")
        print("3. Instale dependências: pip install -r backend/requirements.txt")
        print("4. Inicie o servidor: python backend/start_api.py")
        print("5. Abra http://localhost:8000 e use login.html")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {e}")
        return False

def test_keyauth_connection():
    """Testar conexão KeyAuth com credenciais atuais"""
    print("\n🧪 Testando Conexão KeyAuth...")
    
    try:
        # Tentar importar e testar
        import sys
        sys.path.append('backend')
        
        from auth.keyauth_config import KeyAuthManager
        
        auth_manager = KeyAuthManager()
        print("✅ KeyAuth inicializado com sucesso")
        
        # Testar com uma licença fictícia (vai falhar mas mostra que a conexão funciona)
        result = auth_manager.validate_license("test-license-key")
        
        if not result["valid"]:
            print("✅ Conexão da API KeyAuth funcionando (licença de teste rejeitada como esperado)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("   Certifique-se de instalar as dependências: pip install -r backend/requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        print("   Verifique seu Owner ID e Secret")
        return False

def main():
    """Função principal de configuração"""
    
    # Verificar se já está configurado
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️ Arquivo de configuração já existe!")
        choice = input("Você quer reconfigurar? (s/N): ").strip().lower()
        if choice not in ['s', 'sim', 'y', 'yes']:
            print("Configuração cancelada")
            return
    
    # Configurar credenciais
    if setup_keyauth_credentials():
        
        # Perguntar se o usuário quer testar a conexão
        test = input("\nTestar conexão KeyAuth agora? (S/n): ").strip().lower()
        if test not in ['n', 'nao', 'no']:
            test_keyauth_connection()
        
        print(f"\n🎉 Configuração KeyAuth concluída!")
        print(f"📁 Configuração salva em: {env_file.absolute()}")
        print(f"🔒 Mantenha suas credenciais seguras!")

if __name__ == "__main__":
    main()
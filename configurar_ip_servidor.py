#!/usr/bin/env python3
"""
Configurador automático de IP do servidor SECRIMPO
Atualiza automaticamente os arquivos com o IP correto
"""

import socket
import subprocess
import platform
import os
from pathlib import Path

def get_local_ip():
    """Obtém o IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def update_file_ip(file_path, old_pattern, new_pattern):
    """Atualiza IP em um arquivo"""
    try:
        if not os.path.exists(file_path):
            print(f"⚠️  Arquivo não encontrado: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_pattern in content:
            new_content = content.replace(old_pattern, new_pattern)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Atualizado: {file_path}")
            return True
        else:
            print(f"⚠️  Padrão não encontrado em: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atualizar {file_path}: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CONFIGURADOR DE IP DO SERVIDOR SECRIMPO")
    print("=" * 50)
    
    # Descobrir IP
    server_ip = get_local_ip()
    hostname = socket.gethostname()
    
    print(f"🖥️  Máquina: {hostname}")
    print(f"📍 IP encontrado: {server_ip}")
    print(f"🌐 URL do servidor: http://{server_ip}:8001")
    print()
    
    # Confirmar com usuário
    print("🤔 Este IP está correto?")
    print("   1. Sim, usar este IP")
    print("   2. Não, digitar manualmente")
    print("   3. Usar apenas local (127.0.0.1)")
    
    choice = input("\nEscolha (1-3): ").strip()
    
    if choice == "2":
        server_ip = input("Digite o IP do servidor: ").strip()
        if not server_ip:
            print("❌ IP inválido")
            return
    elif choice == "3":
        server_ip = "127.0.0.1"
    elif choice != "1":
        print("❌ Opção inválida")
        return
    
    print(f"\n🔄 Configurando IP: {server_ip}")
    print("=" * 30)
    
    # Lista de arquivos para atualizar
    updates = [
        {
            "file": "frontend/src/sync-manager.js",
            "old": "this.serverUrl = 'http://127.0.0.1:8001';",
            "new": f"this.serverUrl = 'http://{server_ip}:8001';"
        },
        {
            "file": "backend/test_sync_system.py",
            "old": 'API_BASE_URL = "http://127.0.0.1:8001"',
            "new": f'API_BASE_URL = "http://{server_ip}:8001"'
        }
    ]
    
    # Tentar outras variações de IP que podem existir
    possible_old_ips = ["127.0.0.1", "localhost", "10.160.215.16", "192.168.1.100", "192.168.0.100"]
    
    success_count = 0
    
    for update in updates:
        file_path = update["file"]
        updated = False
        
        # Tentar atualizar com o padrão exato
        if update_file_ip(file_path, update["old"], update["new"]):
            updated = True
            success_count += 1
        else:
            # Tentar com diferentes IPs antigos
            for old_ip in possible_old_ips:
                if old_ip != server_ip:  # Não substituir pelo mesmo IP
                    old_pattern = update["old"].replace("127.0.0.1", old_ip)
                    if update_file_ip(file_path, old_pattern, update["new"]):
                        updated = True
                        success_count += 1
                        break
        
        if not updated:
            print(f"⚠️  Não foi possível atualizar: {file_path}")
    
    print()
    print("📋 RESUMO DA CONFIGURAÇÃO:")
    print("=" * 30)
    print(f"✅ Arquivos atualizados: {success_count}/{len(updates)}")
    print(f"🌐 IP do servidor: {server_ip}")
    print(f"🔗 URL completa: http://{server_ip}:8001")
    print()
    
    if success_count == len(updates):
        print("🎉 Configuração concluída com sucesso!")
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("1. 🚀 Inicie o servidor:")
        print("   cd backend")
        print("   python basic_sync_server.py")
        print()
        print("2. 🧪 Teste a configuração:")
        print("   cd backend")
        print("   python test_sync_system.py")
        print()
        print("3. 👥 Compartilhe com outros usuários:")
        print(f"   - IP do servidor: {server_ip}")
        print("   - Porta: 8001")
        print("   - URL completa: http://{server_ip}:8001")
        print()
        print("⚠️  IMPORTANTE:")
        print("   - Certifique-se de que o firewall permite conexões na porta 8001")
        print("   - Todos os clientes devem estar na mesma rede")
        print("   - O servidor deve estar sempre rodando para sincronização")
        
    else:
        print("⚠️  Alguns arquivos não foram atualizados.")
        print("   Verifique manualmente os arquivos listados acima.")
    
    print()
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
SECRIMPO - Teste de Conectividade de Rede
Script para testar se outros PCs conseguem acessar a pasta compartilhada
"""
import os
import socket
import subprocess
from pathlib import Path

def get_local_ip():
    """Obtém IP local da máquina"""
    try:
        # Conecta a um endereço externo para descobrir IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def test_ping(ip):
    """Testa conectividade via ping"""
    try:
        # Windows usa -n, Linux usa -c
        param = "-n" if os.name == "nt" else "-c"
        result = subprocess.run(
            ["ping", param, "1", ip], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def test_shared_folder_access(ip, share_name="SecrimpoShared"):
    """Testa acesso à pasta compartilhada"""
    try:
        if os.name == "nt":  # Windows
            share_path = f"\\\\{ip}\\{share_name}"
            return os.path.exists(share_path)
        else:  # Linux
            # Assumindo que está montado em /mnt
            share_path = f"/mnt/{share_name}"
            return os.path.exists(share_path)
    except:
        return False

def scan_network_for_secrimpo():
    """Procura por pastas SECRIMPO na rede local"""
    local_ip = get_local_ip()
    network = '.'.join(local_ip.split('.')[:-1])
    
    print(f"🔍 Procurando SECRIMPO na rede {network}.x...")
    
    found_servers = []
    
    # Testar IPs comuns na rede local
    for i in range(1, 255):
        ip = f"{network}.{i}"
        
        # Pular o próprio IP
        if ip == local_ip:
            continue
        
        print(f"   Testando {ip}...", end="", flush=True)
        
        # Teste rápido de ping
        if test_ping(ip):
            print(" 🟢 Online", end="")
            
            # Testar acesso à pasta compartilhada
            if test_shared_folder_access(ip):
                print(" ✅ SECRIMPO encontrado!")
                found_servers.append(ip)
            else:
                print(" ⚪ Sem SECRIMPO")
        else:
            print(" 🔴 Offline")
    
    return found_servers

def main():
    """Função principal"""
    print("=" * 60)
    print("🌐 SECRIMPO - Teste de Conectividade de Rede")
    print("=" * 60)
    
    # Obter IP local
    local_ip = get_local_ip()
    print(f"📍 Seu IP: {local_ip}")
    
    # Verificar se tem pasta compartilhada local
    local_shared = Path("C:\\SecrimpoShared")
    if local_shared.exists():
        print(f"✅ Pasta local encontrada: {local_shared}")
        print(f"🌐 Outros PCs podem acessar via: \\\\{local_ip}\\SecrimpoShared")
    else:
        print(f"ℹ️  Pasta local não encontrada")
    
    print(f"\n🔍 Opções de Teste:")
    print(f"1. 🎯 Testar IP específico")
    print(f"2. 🔍 Procurar SECRIMPO na rede")
    print(f"3. 📋 Mostrar instruções de compartilhamento")
    print(f"4. ❌ Sair")
    
    while True:
        choice = input(f"\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            ip = input("Digite o IP para testar: ").strip()
            
            print(f"\n🔍 Testando conectividade com {ip}...")
            
            # Teste de ping
            if test_ping(ip):
                print(f"   ✅ Ping OK")
                
                # Teste de pasta compartilhada
                if test_shared_folder_access(ip):
                    print(f"   ✅ Pasta SECRIMPO acessível!")
                    print(f"   📁 Caminho: \\\\{ip}\\SecrimpoShared")
                    
                    # Sugerir configuração
                    print(f"\n💡 Para configurar neste PC:")
                    print(f"   python setup_shared_folder.py")
                    print(f"   Escolha opção 2 e digite: \\\\{ip}\\SecrimpoShared")
                else:
                    print(f"   ❌ Pasta SECRIMPO não encontrada")
                    print(f"   💡 Verifique se a pasta está compartilhada no PC {ip}")
            else:
                print(f"   ❌ Ping falhou - PC não acessível")
        
        elif choice == "2":
            print(f"\n🔍 Procurando servidores SECRIMPO na rede...")
            found = scan_network_for_secrimpo()
            
            if found:
                print(f"\n✅ Servidores SECRIMPO encontrados:")
                for ip in found:
                    print(f"   📍 {ip} - \\\\{ip}\\SecrimpoShared")
                
                print(f"\n💡 Para usar um destes servidores:")
                print(f"   python setup_shared_folder.py")
                print(f"   Escolha opção 2 e digite o caminho desejado")
            else:
                print(f"\n❌ Nenhum servidor SECRIMPO encontrado na rede")
                print(f"💡 Verifique se:")
                print(f"   - Outros PCs têm SECRIMPO instalado")
                print(f"   - Pastas estão compartilhadas corretamente")
                print(f"   - Firewall não está bloqueando")
        
        elif choice == "3":
            print(f"\n📋 Instruções de Compartilhamento:")
            print(f"\n🖥️  No PC Servidor (que tem os dados):")
            print(f"   1. Clique direito em C:\\SecrimpoShared")
            print(f"   2. Propriedades > Compartilhamento")
            print(f"   3. Compartilhamento Avançado")
            print(f"   4. Marque 'Compartilhar esta pasta'")
            print(f"   5. Permissões > Adicionar 'Todos' com 'Controle Total'")
            
            print(f"\n💻 Nos PCs Clientes:")
            print(f"   1. Execute: python setup_shared_folder.py")
            print(f"   2. Escolha opção 2 (Pasta de Rede)")
            print(f"   3. Digite: \\\\{local_ip}\\SecrimpoShared")
            
            print(f"\n🔧 Comandos via PowerShell (Administrador):")
            print(f"   # Compartilhar pasta:")
            print(f"   net share SecrimpoShared=C:\\SecrimpoShared /grant:everyone,full")
            print(f"   ")
            print(f"   # Verificar compartilhamentos:")
            print(f"   net share")
        
        elif choice == "4":
            break
        
        else:
            print("❌ Opção inválida. Digite 1, 2, 3 ou 4.")
    
    print(f"\n👋 Teste de conectividade finalizado!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
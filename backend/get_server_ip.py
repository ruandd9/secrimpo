#!/usr/bin/env python3
"""
Script para descobrir o IP do servidor SECRIMPO
"""

import socket
import subprocess
import platform

def get_local_ip():
    """Obtém o IP local da máquina"""
    try:
        # Conecta a um endereço externo para descobrir o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_all_ips():
    """Obtém todos os IPs da máquina"""
    hostname = socket.gethostname()
    ips = []
    
    try:
        # IP principal
        main_ip = socket.gethostbyname(hostname)
        ips.append(("Principal", main_ip))
    except:
        pass
    
    try:
        # IP local (método alternativo)
        local_ip = get_local_ip()
        if local_ip not in [ip[1] for ip in ips]:
            ips.append(("Local", local_ip))
    except:
        pass
    
    # Tentar obter IPs via comando do sistema
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'IPv4' in line and ':' in line:
                    ip = line.split(':')[1].strip()
                    if ip and ip not in [ip_info[1] for ip_info in ips]:
                        ips.append(("Windows", ip))
        else:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            if result.returncode == 0:
                for ip in result.stdout.strip().split():
                    if ip not in [ip_info[1] for ip_info in ips]:
                        ips.append(("Linux", ip))
    except:
        pass
    
    return ips

def main():
    """Função principal"""
    print("🌐 DESCOBRINDO IP DO SERVIDOR SECRIMPO")
    print("=" * 50)
    
    hostname = socket.gethostname()
    print(f"🖥️  Nome da máquina: {hostname}")
    print(f"💻 Sistema operacional: {platform.system()}")
    print()
    
    ips = get_all_ips()
    
    if ips:
        print("📍 IPs encontrados:")
        for i, (tipo, ip) in enumerate(ips, 1):
            print(f"   {i}. {ip} ({tipo})")
        
        print()
        print("🔧 CONFIGURAÇÃO PARA CLIENTES:")
        print("=" * 50)
        
        # Mostrar o IP mais provável para usar
        main_ip = ips[0][1] if ips else "127.0.0.1"
        
        print(f"📋 Configure os clientes para usar:")
        print(f"   Servidor: http://{main_ip}:8001")
        print()
        
        print("🔧 No arquivo frontend/src/sync-manager.js, altere:")
        print(f"   this.serverUrl = 'http://{main_ip}:8001';")
        print()
        
        print("🔧 No arquivo backend/test_sync_system.py, altere:")
        print(f"   API_BASE_URL = \"http://{main_ip}:8001\"")
        print()
        
        print("⚠️  IMPORTANTE:")
        print("   - O servidor deve estar rodando na máquina com este IP")
        print("   - Verifique se o firewall permite conexões na porta 8001")
        print("   - Todos os clientes devem estar na mesma rede")
        
    else:
        print("❌ Não foi possível descobrir o IP da máquina")
        print("   Use 127.0.0.1 para testes locais")
    
    print()
    print("🚀 Para iniciar o servidor:")
    print("   cd backend")
    print("   python basic_sync_server.py")

if __name__ == "__main__":
    main()
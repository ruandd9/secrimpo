# SECRIMPO - Guia de Sincronização em Rede Local

Este documento descreve as opções técnicas para sincronizar dados do SECRIMPO entre múltiplos usuários em um escritório, sem necessidade de servidor dedicado na nuvem.

## Visão Geral

O SECRIMPO foi desenvolvido inicialmente para uso individual, mas pode ser adaptado para uso multi-usuário em rede local através de duas abordagens principais:

1. **Banco de Dados Compartilhado** - Arquivo SQLite em pasta de rede
2. **Aplicação Master-Slave** - Um PC atua como servidor para os demais

---

## 1. Banco de Dados Compartilhado em Rede Local

### Conceito Técnico

Nesta abordagem, o arquivo `secrimpo.db` (SQLite) é armazenado em uma pasta compartilhada da rede local. Todos os usuários executam a aplicação SECRIMPO em seus PCs, mas apontam para o mesmo arquivo de banco de dados centralizado.

### Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PC Cliente 1  │    │   PC Cliente 2  │    │   PC Cliente 3  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ SECRIMPO    │ │    │ │ SECRIMPO    │ │    │ │ SECRIMPO    │ │
│ │ Frontend    │ │    │ │ Frontend    │ │    │ │ Frontend    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ FastAPI     │ │    │ │ FastAPI     │ │    │ │ FastAPI     │ │
│ │ Backend     │ │    │ │ Backend     │ │    │ │ Backend     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │    Servidor de Arquivos     │
                    │   (Pasta Compartilhada)     │
                    │                             │
                    │  📁 \\servidor\secrimpo\    │
                    │      └── secrimpo.db        │
                    └─────────────────────────────┘
```

### Implementação Técnica

#### Pré-requisitos
- Servidor de arquivos ou PC com pasta compartilhada
- Rede local estável (LAN)
- Permissões de leitura/escrita para todos os usuários
- Windows com compartilhamento SMB ou Linux com Samba

#### Passo 1: Configurar Pasta Compartilhada

**No Servidor de Arquivos (Windows):**
```cmd
# Criar pasta compartilhada
mkdir C:\SecrimpoData
net share SecrimpoData=C:\SecrimpoData /grant:everyone,full

# Definir permissões NTFS
icacls C:\SecrimpoData /grant "Domain Users":(OI)(CI)F
```

**No Servidor de Arquivos (Linux):**
```bash
# Instalar Samba
sudo apt install samba

# Configurar compartilhamento
sudo mkdir /srv/secrimpo
sudo chmod 777 /srv/secrimpo

# Adicionar ao /etc/samba/smb.conf
[secrimpo]
path = /srv/secrimpo
browseable = yes
writable = yes
guest ok = yes
```

#### Passo 2: Modificar Configuração do Backend

**Arquivo: `backend/config.py`**
```python
import os
from pathlib import Path

# Configuração para banco compartilhado
SHARED_NETWORK_PATH = r"\\servidor\SecrimpoData"  # Windows
# SHARED_NETWORK_PATH = "/mnt/secrimpo"           # Linux

# Verificar se pasta de rede está acessível
if os.path.exists(SHARED_NETWORK_PATH):
    DATABASE_URL = f"sqlite:///{SHARED_NETWORK_PATH}/secrimpo.db"
    EXPORTS_DIR = Path(SHARED_NETWORK_PATH) / "exports"
else:
    # Fallback para local se rede não estiver disponível
    DATABASE_URL = "sqlite:///./secrimpo.db"
    EXPORTS_DIR = Path("exports")

# Configurações SQLite para rede
SQLITE_CONFIG = {
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "connect_args": {
        "timeout": 30,
        "check_same_thread": False
    }
}
```

**Arquivo: `backend/app.py`**
```python
from sqlalchemy import create_engine
from backend.config import DATABASE_URL, SQLITE_CONFIG

# Engine com configurações para rede
engine = create_engine(
    DATABASE_URL, 
    echo=True,
    **SQLITE_CONFIG
)
```

#### Passo 3: Configurar WAL Mode (Recomendado)

**Script: `backend/setup_wal.py`**
```python
import sqlite3
import os
from backend.config import SHARED_NETWORK_PATH

def setup_wal_mode():
    """Configura SQLite em modo WAL para melhor concorrência"""
    db_path = os.path.join(SHARED_NETWORK_PATH, "secrimpo.db")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Habilitar WAL mode
        conn.execute("PRAGMA journal_mode=WAL;")
        
        # Configurações de performance
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=10000;")
        conn.execute("PRAGMA temp_store=MEMORY;")
        conn.execute("PRAGMA mmap_size=268435456;")  # 256MB
        
        conn.commit()
        conn.close()
        
        print("[CHECK] WAL mode configurado com sucesso")
        
    except Exception as e:
        print(f"[TIMES] Erro ao configurar WAL: {e}")

if __name__ == "__main__":
    setup_wal_mode()
```

#### Passo 4: Script de Instalação para Clientes

**Script: `install_network_client.py`**
```python
#!/usr/bin/env python3
"""
Script para configurar cliente SECRIMPO em rede
"""
import os
import shutil
from pathlib import Path

def setup_network_client():
    print("[ROCKET] Configurando SECRIMPO para rede local...")
    
    # Verificar conectividade com pasta compartilhada
    network_path = r"\\servidor\SecrimpoData"
    
    if not os.path.exists(network_path):
        print(f"[TIMES] Pasta de rede não acessível: {network_path}")
        print("Verifique:")
        print("1. Conexão de rede")
        print("2. Permissões de acesso")
        print("3. Credenciais de usuário")
        return False
    
    # Mapear unidade de rede (opcional)
    try:
        os.system(f'net use Z: "{network_path}" /persistent:yes')
        print("[CHECK] Unidade Z: mapeada com sucesso")
    except:
        print("[WARNING] Não foi possível mapear unidade Z:")
    
    # Criar arquivo de configuração local
    config_content = f'''
# Configuração de rede SECRIMPO
NETWORK_MODE = True
SHARED_PATH = r"{network_path}"
DATABASE_URL = "sqlite:///{network_path}/secrimpo.db"
'''
    
    with open("backend/network_config.py", "w") as f:
        f.write(config_content)
    
    print("[CHECK] Cliente configurado para rede local")
    return True

if __name__ == "__main__":
    setup_network_client()
```

### Vantagens e Limitações

#### ✅ Vantagens
- **Simplicidade**: Fácil de implementar e entender
- **Sincronização Imediata**: Todos veem as mudanças instantaneamente
- **Backup Centralizado**: Um único ponto de backup
- **Sem Servidor Dedicado**: Usa infraestrutura existente

#### ❌ Limitações
- **Concorrência Limitada**: SQLite suporta ~10 usuários simultâneos
- **Dependência de Rede**: Falhas de rede afetam todos os usuários
- **Risco de Corrupção**: Desconexões durante escrita podem corromper dados
- **Performance**: Latência de rede afeta velocidade das operações

### Monitoramento e Troubleshooting

#### Script de Diagnóstico
**Arquivo: `backend/network_diagnostics.py`**
```python
import os
import sqlite3
import time
from pathlib import Path

def diagnose_network_database():
    """Diagnostica problemas com banco em rede"""
    
    network_path = r"\\servidor\SecrimpoData"
    db_path = os.path.join(network_path, "secrimpo.db")
    
    print("[SEARCH] Diagnóstico de Rede SECRIMPO")
    print("=" * 50)
    
    # Teste 1: Conectividade
    print("\n[NETWORK-WIRED] Testando conectividade...")
    if os.path.exists(network_path):
        print(f"[CHECK] Pasta de rede acessível: {network_path}")
    else:
        print(f"[TIMES] Pasta de rede inacessível: {network_path}")
        return
    
    # Teste 2: Permissões
    print("\n[SHIELD-ALT] Testando permissões...")
    try:
        test_file = os.path.join(network_path, "test_write.tmp")
        with open(test_file, "w") as f:
            f.write("teste")
        os.remove(test_file)
        print("[CHECK] Permissões de escrita OK")
    except Exception as e:
        print(f"[TIMES] Erro de permissões: {e}")
        return
    
    # Teste 3: Banco de dados
    print("\n[DATABASE] Testando banco de dados...")
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master")
        count = cursor.fetchone()[0]
        print(f"[CHECK] Banco acessível, {count} tabelas encontradas")
        
        # Verificar modo WAL
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        print(f"[INFO] Modo do journal: {mode}")
        
        conn.close()
    except Exception as e:
        print(f"[TIMES] Erro no banco: {e}")
    
    # Teste 4: Performance
    print("\n[TACHOMETER-ALT] Testando performance...")
    start_time = time.time()
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM policial")
        conn.close()
        elapsed = time.time() - start_time
        print(f"[CHECK] Query executada em {elapsed:.2f}s")
    except Exception as e:
        print(f"[TIMES] Erro de performance: {e}")

if __name__ == "__main__":
    diagnose_network_database()
```

---

## 2. Aplicação Master-Slave (Um PC como Servidor)

### Conceito Técnico

Nesta abordagem, um PC do escritório atua como servidor, executando a API FastAPI e hospedando o banco de dados. Os demais PCs (clientes) executam apenas o frontend Electron e se conectam à API do PC servidor via rede local.

### Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PC Cliente 1  │    │   PC Cliente 2  │    │   PC Cliente 3  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ SECRIMPO    │ │    │ │ SECRIMPO    │ │    │ │ SECRIMPO    │ │
│ │ Frontend    │ │    │ │ Frontend    │ │    │ │ Frontend    │ │
│ │ (Electron)  │ │    │ │ (Electron)  │ │    │ │ (Electron)  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ HTTP API Calls       │ HTTP API Calls       │ HTTP API Calls
          │ 192.168.1.100:8000   │ 192.168.1.100:8000   │ 192.168.1.100:8000
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │      PC Servidor Master     │
                    │    (192.168.1.100)         │
                    │                             │
                    │ ┌─────────────────────────┐ │
                    │ │    FastAPI Backend      │ │
                    │ │    (Port 8000)          │ │
                    │ └─────────────────────────┘ │
                    │ ┌─────────────────────────┐ │
                    │ │    SQLite Database      │ │
                    │ │    (secrimpo.db)        │ │
                    │ └─────────────────────────┘ │
                    └─────────────────────────────┘
```

### Implementação Técnica

#### Pré-requisitos
- PC servidor com IP fixo na rede local
- Firewall configurado para permitir porta 8000
- Rede local estável (LAN)
- Python instalado no PC servidor
- Node.js instalado nos PCs clientes

#### Passo 1: Configurar PC Servidor

**1.1 Definir IP Fixo**

**Windows:**
```cmd
# Verificar configuração atual
ipconfig /all

# Definir IP fixo via interface gráfica ou PowerShell
netsh interface ip set address "Ethernet" static 192.168.1.100 255.255.255.0 192.168.1.1
```

**Linux:**
```bash
# Editar /etc/netplan/01-netcfg.yaml
network:
  version: 2
  ethernets:
    eth0:
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]

# Aplicar configuração
sudo netplan apply
```

**1.2 Configurar Firewall**

**Windows:**
```cmd
# Permitir porta 8000
netsh advfirewall firewall add rule name="SECRIMPO API" dir=in action=allow protocol=TCP localport=8000

# Ou via interface gráfica do Windows Defender
```

**Linux:**
```bash
# UFW
sudo ufw allow 8000/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

**1.3 Modificar Configuração do Servidor**

**Arquivo: `backend/server_config.py`**
```python
"""
Configuração para PC Servidor Master
"""
import os
from pathlib import Path

# Configurações do servidor
SERVER_MODE = True
SERVER_HOST = "0.0.0.0"  # Aceita conexões de qualquer IP
SERVER_PORT = 8000

# Banco de dados local no servidor
DATABASE_URL = "sqlite:///./secrimpo.db"
EXPORTS_DIR = Path("exports")

# Configurações de segurança
ALLOWED_ORIGINS = [
    "http://192.168.1.*",  # Rede local
    "http://localhost:*",   # Localhost
    "http://127.0.0.1:*"   # Loopback
]

# Configurações de performance
MAX_CONNECTIONS = 50
CONNECTION_TIMEOUT = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "secrimpo_server.log"
```

**1.4 Script de Inicialização do Servidor**

**Arquivo: `backend/start_server.py`**
```python
#!/usr/bin/env python3
"""
Script para iniciar SECRIMPO em modo servidor
"""
import uvicorn
import sys
import os
import socket
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

def check_port_available(port):
    """Verifica se porta está disponível"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", port))
        s.close()
        return True
    except:
        return False

def main():
    """Inicia servidor SECRIMPO"""
    
    print("[ROCKET] Iniciando SECRIMPO Server Mode...")
    print("=" * 50)
    
    # Verificar porta
    if not check_port_available(8000):
        print("[TIMES] Porta 8000 já está em uso!")
        print("Verifique se outro SECRIMPO está rodando")
        sys.exit(1)
    
    # Obter IP local
    local_ip = get_local_ip()
    
    print(f"[SERVER] Servidor iniciando em: {local_ip}:8000")
    print(f"[GLOBE] Acesso externo: http://{local_ip}:8000")
    print(f"[BOOK] Documentação: http://{local_ip}:8000/docs")
    print(f"[CHART-BAR] Status: http://{local_ip}:8000/estatisticas")
    
    print("\n[USERS] Configuração para clientes:")
    print(f"API_BASE = 'http://{local_ip}:8000'")
    
    print(f"\n[BOLT] Pressione Ctrl+C para parar o servidor")
    print("=" * 50)
    
    try:
        # Configurar logging
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s: %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "formatter": "default",
                    "class": "logging.FileHandler",
                    "filename": "secrimpo_server.log",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default", "file"],
            },
        }
        
        # Iniciar servidor
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Desabilitado em modo servidor
            log_config=log_config,
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n[STOP] Servidor parado pelo usuário")
    except Exception as e:
        print(f"[TIMES] Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### Passo 2: Configurar PCs Clientes

**2.1 Versão Cliente do Frontend**

**Arquivo: `frontend/client_config.js`**
```javascript
/**
 * Configuração para cliente SECRIMPO
 */

// Configuração da API
const SERVER_CONFIG = {
    // IP do PC servidor (ajustar conforme necessário)
    API_HOST: '192.168.1.100',
    API_PORT: 8000,
    
    // Timeout para requisições
    REQUEST_TIMEOUT: 30000,
    
    // Retry automático
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000
};

// URL base da API
const API_BASE = `http://${SERVER_CONFIG.API_HOST}:${SERVER_CONFIG.API_PORT}`;

// Função para testar conectividade
async function testConnection() {
    try {
        const response = await fetch(`${API_BASE}/`, {
            method: 'GET',
            timeout: 5000
        });
        
        if (response.ok) {
            console.log('[CHECK] Conexão com servidor OK');
            return true;
        } else {
            console.log('[TIMES] Servidor respondeu com erro:', response.status);
            return false;
        }
    } catch (error) {
        console.log('[TIMES] Erro de conexão:', error.message);
        return false;
    }
}

// Exportar configurações
window.SECRIMPO_CONFIG = {
    API_BASE,
    SERVER_CONFIG,
    testConnection
};
```

**2.2 Modificar Frontend para Modo Cliente**

**Arquivo: `frontend/src/client_app.js`**
```javascript
// Importar configuração do cliente
const { API_BASE, testConnection } = window.SECRIMPO_CONFIG;

// Estado da aplicação (modificado para cliente)
let appState = {
    policiais: [],
    proprietarios: [],
    currentPolicial: null,
    currentProprietario: null,
    itemCount: 1,
    serverConnected: false,
    lastSync: null
};

// Inicialização modificada para cliente
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[ROCKET] Iniciando SECRIMPO Cliente...');
    
    // Testar conexão com servidor
    const connected = await testConnection();
    appState.serverConnected = connected;
    
    if (!connected) {
        showMessage('Não foi possível conectar ao servidor. Verifique a rede.', 'error');
        showOfflineMode();
        return;
    }
    
    // Carrega dados do servidor
    await loadInitialData();
    
    // Configura event listeners
    setupEventListeners();
    
    // Configura data atual
    document.getElementById('dataApreensao').valueAsDate = new Date();
    
    // Iniciar monitoramento de conexão
    startConnectionMonitoring();
    
    console.log('[CHECK] SECRIMPO Cliente carregado com sucesso!');
});

// Monitoramento de conexão
function startConnectionMonitoring() {
    setInterval(async () => {
        const connected = await testConnection();
        
        if (connected !== appState.serverConnected) {
            appState.serverConnected = connected;
            
            if (connected) {
                showMessage('Conexão com servidor restaurada', 'success');
                await loadInitialData(); // Recarregar dados
            } else {
                showMessage('Conexão com servidor perdida', 'error');
            }
        }
    }, 30000); // Verificar a cada 30 segundos
}

// Modo offline (funcionalidade limitada)
function showOfflineMode() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'offline-banner';
    messageDiv.innerHTML = `
        <i class="fas fa-wifi-slash"></i>
        <strong>Modo Offline</strong> - Conecte-se ao servidor para usar o sistema
        <button onclick="location.reload()">Tentar Novamente</button>
    `;
    
    document.body.insertBefore(messageDiv, document.body.firstChild);
}
```

**2.3 Script de Instalação para Clientes**

**Arquivo: `install_client.py`**
```python
#!/usr/bin/env python3
"""
Script para instalar SECRIMPO Cliente
"""
import os
import json
import requests
from pathlib import Path

def discover_server():
    """Tenta descobrir servidor SECRIMPO na rede local"""
    import socket
    
    # Obter rede local
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    network = '.'.join(local_ip.split('.')[:-1])
    
    print(f"[SEARCH] Procurando servidor na rede {network}.x...")
    
    # Testar IPs comuns
    common_ips = [f"{network}.{i}" for i in [1, 100, 101, 102, 200, 254]]
    
    for ip in common_ips:
        try:
            response = requests.get(f"http://{ip}:8000/", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if "SECRIMPO" in data.get("message", ""):
                    print(f"[CHECK] Servidor encontrado em: {ip}:8000")
                    return ip
        except:
            continue
    
    return None

def setup_client():
    """Configura cliente SECRIMPO"""
    print("[ROCKET] Configurando SECRIMPO Cliente...")
    
    # Descobrir servidor automaticamente
    server_ip = discover_server()
    
    if not server_ip:
        print("[TIMES] Servidor não encontrado automaticamente")
        server_ip = input("Digite o IP do servidor SECRIMPO: ")
    
    # Testar conexão
    try:
        response = requests.get(f"http://{server_ip}:8000/", timeout=5)
        if response.status_code != 200:
            raise Exception("Servidor não respondeu corretamente")
        print(f"[CHECK] Conexão com {server_ip}:8000 OK")
    except Exception as e:
        print(f"[TIMES] Erro ao conectar: {e}")
        return False
    
    # Criar configuração
    config = {
        "API_HOST": server_ip,
        "API_PORT": 8000,
        "CLIENT_MODE": True,
        "SERVER_URL": f"http://{server_ip}:8000"
    }
    
    # Salvar configuração
    config_path = Path("frontend/client_config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"[CHECK] Cliente configurado para servidor: {server_ip}:8000")
    print("\n[INFO] Próximos passos:")
    print("1. cd frontend")
    print("2. npm start")
    
    return True

if __name__ == "__main__":
    setup_client()
```

#### Passo 3: Monitoramento e Administração

**3.1 Dashboard do Servidor**

**Arquivo: `backend/admin_dashboard.py`**
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import psutil
import sqlite3
from datetime import datetime

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard():
    """Dashboard administrativo do servidor"""
    
    # Estatísticas do sistema
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Estatísticas do banco
    conn = sqlite3.connect("secrimpo.db")
    cursor = conn.cursor()
    
    stats = {}
    tables = ['policial', 'proprietario', 'ocorrencia', 'item_apreendido']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    
    conn.close()
    
    # HTML do dashboard
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SECRIMPO Server Dashboard</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .card {{ background: #f5f5f5; padding: 20px; margin: 10px; border-radius: 8px; }}
            .metric {{ display: inline-block; margin: 10px; }}
            .status-ok {{ color: green; }}
            .status-warning {{ color: orange; }}
            .status-error {{ color: red; }}
        </style>
    </head>
    <body>
        <h1><i class="fas fa-server"></i> SECRIMPO Server Dashboard</h1>
        
        <div class="card">
            <h2><i class="fas fa-chart-line"></i> Sistema</h2>
            <div class="metric">
                <i class="fas fa-microchip"></i> CPU: {cpu_percent}%
            </div>
            <div class="metric">
                <i class="fas fa-memory"></i> RAM: {memory.percent}%
            </div>
            <div class="metric">
                <i class="fas fa-hdd"></i> Disco: {disk.percent}%
            </div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-database"></i> Banco de Dados</h2>
            <div class="metric">
                <i class="fas fa-user-shield"></i> Policiais: {stats['policial']}
            </div>
            <div class="metric">
                <i class="fas fa-user"></i> Proprietários: {stats['proprietario']}
            </div>
            <div class="metric">
                <i class="fas fa-clipboard-list"></i> Ocorrências: {stats['ocorrencia']}
            </div>
            <div class="metric">
                <i class="fas fa-box"></i> Itens: {stats['item_apreendido']}
            </div>
        </div>
        
        <div class="card">
            <h2><i class="fas fa-clock"></i> Última Atualização</h2>
            <p>{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <script>
            // Auto-refresh a cada 30 segundos
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """
    
    return html
```

### Vantagens e Limitações

#### ✅ Vantagens
- **Melhor Performance**: API centralizada otimizada
- **Controle de Concorrência**: FastAPI gerencia múltiplos usuários
- **Escalabilidade**: Suporta mais usuários simultâneos
- **Monitoramento**: Dashboard administrativo centralizado
- **Backup Simplificado**: Dados centralizados em um PC
- **Atualizações**: Fácil atualizar apenas o servidor

#### ❌ Limitações
- **Ponto Único de Falha**: Se PC servidor falhar, sistema para
- **Dependência de Rede**: Clientes precisam de conectividade constante
- **Recursos do Servidor**: PC servidor precisa estar sempre ligado
- **Configuração Inicial**: Mais complexa que banco compartilhado

### Recomendações de Hardware

#### PC Servidor (Mínimo)
- **CPU**: Intel i3 ou AMD Ryzen 3
- **RAM**: 8GB DDR4
- **Storage**: SSD 256GB
- **Rede**: Ethernet Gigabit

#### PC Servidor (Recomendado)
- **CPU**: Intel i5 ou AMD Ryzen 5
- **RAM**: 16GB DDR4
- **Storage**: SSD 512GB
- **Rede**: Ethernet Gigabit
- **UPS**: No-break para evitar paradas

#### Rede
- **Switch**: Gigabit Ethernet
- **Cabeamento**: Cat 6 ou superior
- **Largura de Banda**: Mínimo 100Mbps por cliente

---

## Comparação das Abordagens

| Critério | Banco Compartilhado | Master-Slave |
|----------|-------------------|--------------|
| **Complexidade** | Baixa | Média |
| **Performance** | Limitada | Boa |
| **Usuários Simultâneos** | ~10 | ~50 |
| **Ponto de Falha** | Rede/Arquivo | PC Servidor |
| **Backup** | Simples | Simples |
| **Manutenção** | Baixa | Média |
| **Escalabilidade** | Limitada | Boa |
| **Custo** | Baixo | Baixo |

## Recomendações Finais

### Para Escritórios Pequenos (2-5 usuários):
- **Recomendado**: Banco Compartilhado
- **Motivo**: Simplicidade e baixo custo

### Para Escritórios Médios (5-15 usuários):
- **Recomendado**: Master-Slave
- **Motivo**: Melhor performance e controle

### Para Escritórios Grandes (15+ usuários):
- **Recomendado**: Migrar para PostgreSQL/MySQL
- **Motivo**: Banco dedicado para alta concorrência

---

*Este documento deve ser atualizado conforme a evolução do sistema e feedback dos usuários.*
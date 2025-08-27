"""
Configurações da API SECRIMPO
"""
import os
import json
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"

# Configuração de armazenamento compartilhado
def get_storage_config():
    """Obtém configuração de armazenamento (compartilhado ou local)"""
    try:
        # Tentar carregar configuração de armazenamento compartilhado
        shared_config_path = Path(__file__).parent.parent / "shared_config.json"
        
        if shared_config_path.exists():
            with open(shared_config_path, "r") as f:
                config = json.load(f)
            
            # Importar aqui para evitar dependência circular
            from shared_storage import SharedStorageManager
            storage = SharedStorageManager(config.get("shared_path"))
            
            # Testar conectividade
            is_connected, message = storage.test_connectivity()
            
            if is_connected:
                print(f"[CHECK] Usando armazenamento compartilhado: {storage.shared_path}")
                return {
                    "database_url": f"sqlite:///{storage.get_database_path()}",
                    "database_dir": storage.shared_path / "database",
                    "exports_dir": storage.get_exports_path(),
                    "shared_mode": True,
                    "storage_manager": storage
                }
            else:
                print(f"[WARNING] Armazenamento compartilhado inacessível: {message}")
                print("[INFO] Usando modo local como fallback")
        
        # Fallback para modo local
        print("[INFO] Usando armazenamento local")
        database_dir = BASE_DIR / "database"
        exports_dir = BASE_DIR / "exports"
        
        # Criar diretórios locais
        database_dir.mkdir(exist_ok=True)
        exports_dir.mkdir(exist_ok=True)
        
        return {
            "database_url": f"sqlite:///{database_dir}/secrimpo.db",
            "database_dir": database_dir,
            "exports_dir": exports_dir,
            "shared_mode": False,
            "storage_manager": None
        }
        
    except Exception as e:
        print(f"[ERROR] Erro na configuração de armazenamento: {e}")
        # Fallback para local em caso de erro
        database_dir = BASE_DIR / "database"
        exports_dir = BASE_DIR / "exports"
        
        database_dir.mkdir(exist_ok=True)
        exports_dir.mkdir(exist_ok=True)
        
        return {
            "database_url": f"sqlite:///{database_dir}/secrimpo.db",
            "database_dir": database_dir,
            "exports_dir": exports_dir,
            "shared_mode": False,
            "storage_manager": None
        }

# Obter configuração de armazenamento
STORAGE_CONFIG = get_storage_config()

# Configurações do banco de dados
DATABASE_URL = STORAGE_CONFIG["database_url"]
DATABASE_DIR = STORAGE_CONFIG["database_dir"]
EXPORTS_DIR = STORAGE_CONFIG["exports_dir"]
SHARED_MODE = STORAGE_CONFIG["shared_mode"]
STORAGE_MANAGER = STORAGE_CONFIG["storage_manager"]

DATABASE_ECHO = True  # Para debug, desabilitar em produção

# Configurações SQLite para rede (se em modo compartilhado)
if SHARED_MODE:
    SQLITE_CONFIG = {
        "pool_timeout": 30,
        "pool_recycle": 3600,
        "connect_args": {
            "timeout": 30,
            "check_same_thread": False
        }
    }
else:
    SQLITE_CONFIG = {
        "connect_args": {
            "check_same_thread": False
        }
    }

# Configurações da API
API_HOST = "127.0.0.1"
API_PORT = 8000
API_RELOAD = True  # Para desenvolvimento

# Configurações CORS
CORS_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
    "http://localhost:8080",  # Vue dev server
    "http://127.0.0.1:8080",
    "*"  # Para desenvolvimento - remover em produção
]

# Configurações de exportação
EXPORT_MAX_RECORDS = 10000  # Limite máximo de registros por exportação
EXPORT_FORMATS = ["xlsx", "csv"]  # Formatos suportados

# Configurações de paginação
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000

# Unidades disponíveis para seleção
UNIDADES_DISPONIVEIS = [
    "8ª CPR",
    "10ª CPR", 
    "16ª CPR"
]

# Configurações de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Criar diretórios se não existirem
EXPORTS_DIR.mkdir(exist_ok=True)
DATABASE_DIR.mkdir(exist_ok=True)

# Configurações específicas do ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    DATABASE_ECHO = False
    API_RELOAD = False
    CORS_ORIGINS = []  # Definir origens específicas em produção
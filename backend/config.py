"""
Configurações da API SECRIMPO
"""
import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DATABASE_DIR = BASE_DIR / "database"
EXPORTS_DIR = BASE_DIR / "exports"
MODELS_DIR = BASE_DIR / "models"

# Configurações do banco de dados
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/secrimpo.db"
DATABASE_ECHO = True  # Para debug, desabilitar em produção

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
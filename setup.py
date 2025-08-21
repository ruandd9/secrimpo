#!/usr/bin/env python3
"""
Script de setup para SECRIMPO
Instala todas as dependências e configura o ambiente
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            print(f"[TIMES] Erro ao executar: {command}")
            print(f"Erro: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"[TIMES] Erro inesperado: {e}")
        return False

def check_requirements():
    """Verifica se os pré-requisitos estão instalados"""
    print("[SEARCH] Verificando pré-requisitos...")
    
    # Verifica Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            print("[TIMES] Python 3.8+ é necessário")
            return False
        print(f"[CHECK] Python {python_version.major}.{python_version.minor} encontrado")
    except:
        print("[TIMES] Python não encontrado")
        return False
    
    # Verifica Node.js
    if not run_command("node --version"):
        print("[TIMES] Node.js não encontrado. Instale Node.js 16+ primeiro.")
        return False
    print("[CHECK] Node.js encontrado")
    
    # Verifica npm
    if not run_command("npm --version"):
        print("[TIMES] npm não encontrado")
        return False
    print("[CHECK] npm encontrado")
    
    return True

def setup_backend():
    """Configura o backend Python"""
    print("\n[PYTHON] Configurando backend Python...")
    
    backend_path = Path("backend")
    if not backend_path.exists():
        print("[TIMES] Pasta backend não encontrada")
        return False
    
    # Instala dependências Python
    print("[BOX] Instalando dependências Python...")
    if not run_command("pip install -r requirements.txt", cwd=backend_path):
        print("[TIMES] Falha ao instalar dependências Python")
        return False
    
    print("[CHECK] Backend configurado com sucesso")
    return True

def setup_frontend():
    """Configura o frontend Electron"""
    print("\n[BOLT] Configurando frontend Electron...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("[TIMES] Pasta frontend não encontrada")
        return False
    
    # Instala dependências Node.js
    print("[BOX] Instalando dependências Node.js...")
    if not run_command("npm install", cwd=frontend_path):
        print("[TIMES] Falha ao instalar dependências Node.js")
        return False
    
    print("[CHECK] Frontend configurado com sucesso")
    return True

def create_directories():
    """Cria diretórios necessários"""
    print("\n[FOLDER] Criando diretórios...")
    
    directories = [
        "backend/exports",
        "frontend/assets",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"[CHECK] Diretório criado: {directory}")

def test_installation():
    """Testa se a instalação foi bem-sucedida"""
    print("\n[FLASK] Testando instalação...")
    
    # Testa imports Python
    try:
        import fastapi
        import sqlalchemy
        import pandas
        print("[CHECK] Dependências Python OK")
    except ImportError as e:
        print(f"[TIMES] Erro nas dependências Python: {e}")
        return False
    
    return True

def main():
    """Função principal do setup"""
    print("[ROCKET] SECRIMPO - Setup Automático")
    print("=" * 40)
    
    # Verifica pré-requisitos
    if not check_requirements():
        print("\n[TIMES] Setup falhou. Instale os pré-requisitos primeiro.")
        sys.exit(1)
    
    # Cria diretórios
    create_directories()
    
    # Configura backend
    if not setup_backend():
        print("\n[TIMES] Setup do backend falhou")
        sys.exit(1)
    
    # Configura frontend
    if not setup_frontend():
        print("\n[TIMES] Setup do frontend falhou")
        sys.exit(1)
    
    # Testa instalação
    if not test_installation():
        print("\n[TIMES] Teste da instalação falhou")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("[CHECK] SECRIMPO configurado com sucesso!")
    print("\n[CLIPBOARD-LIST] Próximos passos:")
    print("1. Inicie o backend: cd backend && python start_api.py")
    print("2. Inicie o frontend: cd frontend && npm start")
    print("3. Ou use: npm run start (inicia ambos)")
    print("\n[PARTY] Bom trabalho!")

if __name__ == "__main__":
    main()
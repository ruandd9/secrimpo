#!/usr/bin/env python3
"""
Script para iniciar o servidor SECRIMPO
"""

import os
import sys
import uvicorn

# Mudar para o diretório backend
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("🚀 Iniciando servidor SECRIMPO...")
    print("📍 URL: http://127.0.0.1:8000")
    print("🔑 Modo: Demo (KeyAuth não configurado)")
    print("📱 Frontend: Abra frontend/src/login.html no navegador")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("\n" + "="*50)
    
    try:
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

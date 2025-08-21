#!/usr/bin/env python3
"""
Script para inicializar a API SECRIMPO
"""
import uvicorn
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Inicia o servidor FastAPI"""
    print("🚀 Iniciando SECRIMPO API...")
    print("📍 Servidor rodando em: http://127.0.0.1:8000")
    print("📚 Documentação em: http://127.0.0.1:8000/docs")
    print("🔧 Redoc em: http://127.0.0.1:8000/redoc")
    print("\n⚡ Pressione Ctrl+C para parar o servidor\n")
    
    try:
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_dirs=["backend", "models", "database"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
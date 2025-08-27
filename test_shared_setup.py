#!/usr/bin/env python3
"""
SECRIMPO - Teste de Configuração Compartilhada
Script para testar se a pasta compartilhada está funcionando corretamente
"""
import sys
import os
from pathlib import Path
import json
import sqlite3
from datetime import datetime

def test_shared_configuration():
    """Testa configuração compartilhada completa"""
    print("=" * 60)
    print("🧪 SECRIMPO - Teste de Configuração Compartilhada")
    print("=" * 60)
    
    # Verificar estrutura do projeto
    if not Path("backend").exists():
        print("❌ Pasta 'backend' não encontrada")
        print("   Execute este script na pasta raiz do projeto SECRIMPO")
        return False
    
    # Adicionar backend ao path
    sys.path.append(str(Path("backend").absolute()))
    
    try:
        # Teste 1: Importar módulos
        print("\n1️⃣  Testando importação de módulos...")
        
        from shared_storage import SharedStorageManager
        print("   ✅ shared_storage.py importado")
        
        from config import DATABASE_URL, SHARED_MODE, EXPORTS_DIR
        print("   ✅ config.py importado")
        
        # Teste 2: Verificar configuração
        print("\n2️⃣  Verificando configuração...")
        print(f"   📊 Banco de dados: {DATABASE_URL}")
        print(f"   🗂️  Modo compartilhado: {SHARED_MODE}")
        print(f"   📤 Pasta de exportações: {EXPORTS_DIR}")
        
        if SHARED_MODE:
            print("   ✅ Modo compartilhado ativo")
        else:
            print("   ℹ️  Modo local ativo (normal se não configurou pasta compartilhada)")
        
        # Teste 3: Testar armazenamento
        print("\n3️⃣  Testando armazenamento...")
        
        if SHARED_MODE:
            # Carregar configuração compartilhada
            config_file = Path("shared_config.json")
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = json.load(f)
                
                storage = SharedStorageManager(config["shared_path"])
                
                # Testar conectividade
                is_connected, message = storage.test_connectivity()
                if is_connected:
                    print(f"   ✅ {message}")
                else:
                    print(f"   ❌ {message}")
                    return False
                
                # Verificar estrutura de pastas
                required_folders = ["database", "exports", "backups", "logs"]
                for folder in required_folders:
                    folder_path = storage.shared_path / folder
                    if folder_path.exists():
                        print(f"   ✅ Pasta {folder} existe")
                    else:
                        print(f"   ❌ Pasta {folder} não encontrada")
                        return False
                
            else:
                print("   ❌ Arquivo shared_config.json não encontrado")
                return False
        else:
            print("   ℹ️  Testando armazenamento local...")
            if Path("backend/secrimpo.db").exists():
                print("   ✅ Banco local encontrado")
            else:
                print("   ℹ️  Banco local será criado na primeira execução")
        
        # Teste 4: Testar banco de dados
        print("\n4️⃣  Testando banco de dados...")
        
        # Extrair caminho do banco da URL
        if DATABASE_URL.startswith("sqlite:///"):
            db_path = DATABASE_URL.replace("sqlite:///", "")
            
            # Resolver caminho absoluto se necessário
            if not os.path.isabs(db_path):
                db_path = os.path.abspath(db_path)
            
            print(f"   📍 Caminho do banco: {db_path}")
            
            if os.path.exists(db_path):
                print("   ✅ Arquivo do banco existe")
                
                # Testar conexão
                try:
                    conn = sqlite3.connect(db_path, timeout=10)
                    cursor = conn.cursor()
                    
                    # Verificar tabelas
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    expected_tables = ['policial', 'proprietario', 'ocorrencia', 'item_apreendido']
                    
                    for table in expected_tables:
                        if table in tables:
                            print(f"   ✅ Tabela {table} existe")
                        else:
                            print(f"   ⚠️  Tabela {table} não encontrada (será criada na primeira execução)")
                    
                    # Verificar modo WAL
                    cursor.execute("PRAGMA journal_mode")
                    mode = cursor.fetchone()[0]
                    print(f"   📝 Modo do journal: {mode}")
                    
                    conn.close()
                    print("   ✅ Conexão com banco OK")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao conectar com banco: {e}")
                    return False
            else:
                print("   ℹ️  Banco será criado na primeira execução da API")
        
        # Teste 5: Testar API (se possível)
        print("\n5️⃣  Testando configuração da API...")
        
        try:
            # Importar app para verificar se carrega sem erros
            from app import app, engine
            print("   ✅ Aplicação FastAPI carregada")
            
            # Testar engine do SQLAlchemy
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                print("   ✅ Engine SQLAlchemy funcionando")
            
        except ImportError as e:
            print(f"   ⚠️  Aviso: Não foi possível importar API: {e}")
            print("   ℹ️  Isso é normal se as dependências não estão instaladas")
            print("   💡 Execute: pip install -r backend/requirements.txt")
            # Não retornar False aqui, pois o resto pode estar funcionando
        except Exception as e:
            print(f"   ❌ Erro ao carregar API: {e}")
            return False
        
        # Teste 6: Resumo final
        print("\n6️⃣  Resumo dos Testes")
        
        if SHARED_MODE:
            print("   🎯 Modo: Compartilhado")
            print(f"   📁 Pasta: {storage.shared_path}")
            print(f"   📊 Banco: {storage.get_database_path()}")
            print(f"   📤 Exports: {storage.get_exports_path()}")
        else:
            print("   🎯 Modo: Local")
            print(f"   📊 Banco: {DATABASE_URL}")
            print(f"   📤 Exports: {EXPORTS_DIR}")
        
        print("\n✅ Todos os testes passaram!")
        print("\n📝 Próximos passos:")
        print("1. Inicie a API: python backend/start_api.py")
        print("2. Inicie o frontend: cd frontend && npm start")
        print("3. Teste criando uma ocorrência")
        
        if SHARED_MODE:
            print("4. Teste em outro PC para verificar sincronização")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n💡 Soluções:")
        print("1. Instale as dependências: pip install -r backend/requirements.txt")
        print("2. Verifique se está na pasta correta do projeto")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def create_test_data():
    """Cria dados de teste para verificar funcionamento"""
    print("\n🧪 Criando dados de teste...")
    
    try:
        sys.path.append(str(Path("backend").absolute()))
        from app import SessionLocal, Policial, Proprietario, Ocorrencia, ItemApreendido
        from datetime import date
        
        db = SessionLocal()
        
        # Verificar se já existem dados
        if db.query(Policial).count() > 0:
            print("   ℹ️  Dados de teste já existem")
            db.close()
            return True
        
        # Criar policial de teste
        policial_teste = Policial(
            nome="João Silva (TESTE)",
            matricula="TEST001",
            graduacao="Soldado",
            unidade="8ª CPR"
        )
        db.add(policial_teste)
        db.commit()
        db.refresh(policial_teste)
        print("   ✅ Policial de teste criado")
        
        # Criar proprietário de teste
        proprietario_teste = Proprietario(
            nome="Maria Santos (TESTE)",
            documento="12345678900"
        )
        db.add(proprietario_teste)
        db.commit()
        db.refresh(proprietario_teste)
        print("   ✅ Proprietário de teste criado")
        
        # Criar ocorrência de teste
        ocorrencia_teste = Ocorrencia(
            numero_genesis="TEST2024001",
            unidade_fato="Centro (TESTE)",
            data_apreensao=date.today(),
            lei_infringida="Lei 11.343/06 (TESTE)",
            artigo="Art. 28 (TESTE)",
            policial_condutor_id=policial_teste.id
        )
        db.add(ocorrencia_teste)
        db.commit()
        db.refresh(ocorrencia_teste)
        print("   ✅ Ocorrência de teste criada")
        
        # Criar item de teste
        item_teste = ItemApreendido(
            especie="Entorpecente (TESTE)",
            item="Maconha (TESTE)",
            quantidade=1,
            descricao_detalhada="Pequena porção para teste do sistema",
            ocorrencia_id=ocorrencia_teste.id,
            proprietario_id=proprietario_teste.id,
            policial_id=policial_teste.id
        )
        db.add(item_teste)
        db.commit()
        print("   ✅ Item de teste criado")
        
        db.close()
        
        print("   🎉 Dados de teste criados com sucesso!")
        print("   ⚠️  Lembre-se de remover os dados de teste em produção")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao criar dados de teste: {e}")
        return False

def main():
    """Função principal"""
    try:
        # Executar testes
        success = test_shared_configuration()
        
        if success:
            # Perguntar se quer criar dados de teste
            print("\n" + "="*60)
            create_test = input("Deseja criar dados de teste? (s/N): ").strip().lower()
            
            if create_test in ['s', 'sim', 'y', 'yes']:
                create_test_data()
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste cancelado pelo usuário")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎉 Configuração testada com sucesso!")
    else:
        print(f"\n❌ Problemas encontrados na configuração")
    
    input("\nPressione Enter para sair...")
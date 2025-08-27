#!/usr/bin/env python3
"""
SECRIMPO - Diagnóstico de Pasta Compartilhada
Script para verificar status e resolver problemas com armazenamento compartilhado
"""
import os
import sqlite3
import time
import json
from pathlib import Path
from datetime import datetime

def test_database_performance(db_path, num_tests=5):
    """Testa performance do banco de dados"""
    print(f"\n🏃 Testando performance do banco...")
    
    times = []
    for i in range(num_tests):
        start_time = time.time()
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master")
            result = cursor.fetchone()
            conn.close()
            elapsed = time.time() - start_time
            times.append(elapsed)
            print(f"   Teste {i+1}: {elapsed:.3f}s")
        except Exception as e:
            print(f"   Teste {i+1}: ERRO - {e}")
            return None
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"   ⏱️  Tempo médio: {avg_time:.3f}s")
        
        if avg_time < 0.1:
            print(f"   ✅ Performance excelente")
        elif avg_time < 0.5:
            print(f"   ✅ Performance boa")
        elif avg_time < 1.0:
            print(f"   ⚠️  Performance aceitável")
        else:
            print(f"   ❌ Performance ruim - verifique rede")
        
        return avg_time
    
    return None

def check_database_integrity(db_path):
    """Verifica integridade do banco de dados"""
    print(f"\n🔍 Verificando integridade do banco...")
    
    try:
        conn = sqlite3.connect(str(db_path), timeout=30)
        cursor = conn.cursor()
        
        # Verificar integridade
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        
        if result[0] == "ok":
            print(f"   ✅ Integridade OK")
        else:
            print(f"   ❌ Problemas de integridade: {result[0]}")
            return False
        
        # Verificar modo WAL
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        print(f"   📝 Modo do journal: {mode}")
        
        if mode.upper() == "WAL":
            print(f"   ✅ WAL mode ativo (melhor para concorrência)")
        else:
            print(f"   ⚠️  WAL mode inativo (pode afetar concorrência)")
        
        # Verificar estatísticas das tabelas
        tables = ['policial', 'proprietario', 'ocorrencia', 'item_apreendido']
        print(f"   📊 Estatísticas das tabelas:")
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"      {table}: {count} registros")
            except sqlite3.OperationalError:
                print(f"      {table}: tabela não existe")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar integridade: {e}")
        return False

def check_file_permissions(path):
    """Verifica permissões de arquivo/pasta"""
    print(f"\n🔐 Verificando permissões...")
    
    try:
        # Teste de leitura
        if os.access(path, os.R_OK):
            print(f"   ✅ Permissão de leitura OK")
        else:
            print(f"   ❌ Sem permissão de leitura")
            return False
        
        # Teste de escrita
        if os.access(path, os.W_OK):
            print(f"   ✅ Permissão de escrita OK")
        else:
            print(f"   ❌ Sem permissão de escrita")
            return False
        
        # Teste prático de escrita
        test_file = Path(path) / "test_permissions.tmp"
        try:
            with open(test_file, "w") as f:
                f.write("teste de permissões")
            test_file.unlink()
            print(f"   ✅ Teste prático de escrita OK")
        except Exception as e:
            print(f"   ❌ Erro no teste de escrita: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar permissões: {e}")
        return False

def check_network_connectivity(path):
    """Verifica conectividade de rede (se aplicável)"""
    path_str = str(path)
    
    # Verificar se é caminho de rede
    is_network = (
        path_str.startswith("\\\\") or  # Windows UNC
        path_str.startswith("//") or    # Linux SMB
        ":" in path_str and len(path_str.split(":")[0]) == 1  # Unidade mapeada
    )
    
    if not is_network:
        print(f"\n🌐 Caminho local detectado - pular teste de rede")
        return True
    
    print(f"\n🌐 Testando conectividade de rede...")
    
    try:
        # Teste básico de acesso
        if os.path.exists(path):
            print(f"   ✅ Caminho de rede acessível")
        else:
            print(f"   ❌ Caminho de rede inacessível")
            return False
        
        # Teste de latência
        start_time = time.time()
        list(Path(path).iterdir())
        latency = time.time() - start_time
        
        print(f"   ⏱️  Latência de listagem: {latency:.3f}s")
        
        if latency < 0.1:
            print(f"   ✅ Latência excelente")
        elif latency < 0.5:
            print(f"   ✅ Latência boa")
        elif latency < 1.0:
            print(f"   ⚠️  Latência aceitável")
        else:
            print(f"   ❌ Latência alta - verifique rede")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro de conectividade: {e}")
        return False

def generate_report(storage_manager):
    """Gera relatório completo de diagnóstico"""
    print(f"\n📋 Gerando relatório de diagnóstico...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "shared_path": str(storage_manager.shared_path),
        "database_path": str(storage_manager.get_database_path()),
        "exports_path": str(storage_manager.get_exports_path()),
        "tests": {}
    }
    
    # Teste de conectividade
    is_connected, message = storage_manager.test_connectivity()
    report["tests"]["connectivity"] = {
        "status": "OK" if is_connected else "ERRO",
        "message": message
    }
    
    # Teste de permissões
    permissions_ok = check_file_permissions(storage_manager.shared_path)
    report["tests"]["permissions"] = {
        "status": "OK" if permissions_ok else "ERRO"
    }
    
    # Teste de rede
    network_ok = check_network_connectivity(storage_manager.shared_path)
    report["tests"]["network"] = {
        "status": "OK" if network_ok else "ERRO"
    }
    
    # Teste de integridade do banco
    db_path = storage_manager.get_database_path()
    if db_path.exists():
        integrity_ok = check_database_integrity(db_path)
        report["tests"]["database_integrity"] = {
            "status": "OK" if integrity_ok else "ERRO"
        }
        
        # Teste de performance
        performance = test_database_performance(db_path)
        report["tests"]["database_performance"] = {
            "status": "OK" if performance and performance < 1.0 else "ERRO",
            "avg_time": performance
        }
    else:
        report["tests"]["database_integrity"] = {
            "status": "ERRO",
            "message": "Banco de dados não encontrado"
        }
    
    # Salvar relatório
    report_path = storage_manager.shared_path / "logs" / f"diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"   ✅ Relatório salvo: {report_path}")
    
    return report

def main():
    """Função principal de diagnóstico"""
    print("=" * 70)
    print("🔍 SECRIMPO - Diagnóstico de Pasta Compartilhada")
    print("=" * 70)
    
    # Verificar se existe configuração
    config_file = Path("shared_config.json")
    if not config_file.exists():
        print("❌ Configuração de pasta compartilhada não encontrada")
        print("   Execute primeiro: python setup_shared_folder.py")
        return False
    
    try:
        # Carregar configuração
        with open(config_file, "r") as f:
            config = json.load(f)
        
        print(f"📁 Pasta compartilhada: {config['shared_path']}")
        print(f"📅 Configurada em: {config.get('setup_date', 'N/A')}")
        
        # Importar gerenciador
        from shared_storage import SharedStorageManager
        storage = SharedStorageManager(config["shared_path"])
        
        print(f"\n🔍 Iniciando diagnóstico completo...")
        
        # Teste 1: Conectividade básica
        print(f"\n1️⃣  Teste de Conectividade")
        is_connected, message = storage.test_connectivity()
        
        if is_connected:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
            print(f"\n💡 Soluções sugeridas:")
            print(f"   - Verifique se a pasta existe: {storage.shared_path}")
            print(f"   - Confirme permissões de acesso")
            print(f"   - Teste conectividade de rede")
            return False
        
        # Teste 2: Permissões
        print(f"\n2️⃣  Teste de Permissões")
        permissions_ok = check_file_permissions(storage.shared_path)
        
        # Teste 3: Conectividade de rede
        print(f"\n3️⃣  Teste de Rede")
        network_ok = check_network_connectivity(storage.shared_path)
        
        # Teste 4: Banco de dados
        db_path = storage.get_database_path()
        if db_path.exists():
            print(f"\n4️⃣  Teste do Banco de Dados")
            integrity_ok = check_database_integrity(db_path)
            
            print(f"\n5️⃣  Teste de Performance")
            performance_ok = test_database_performance(db_path)
        else:
            print(f"\n4️⃣  ❌ Banco de dados não encontrado: {db_path}")
            print(f"   Execute: python backend/shared_storage.py")
            integrity_ok = False
            performance_ok = False
        
        # Gerar relatório
        print(f"\n6️⃣  Relatório Final")
        report = generate_report(storage)
        
        # Resumo final
        print(f"\n📊 Resumo do Diagnóstico:")
        all_tests = [is_connected, permissions_ok, network_ok, integrity_ok, bool(performance_ok)]
        passed_tests = sum(all_tests)
        total_tests = len(all_tests)
        
        print(f"   ✅ Testes aprovados: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print(f"   🎉 Sistema funcionando perfeitamente!")
        elif passed_tests >= total_tests * 0.8:
            print(f"   ⚠️  Sistema funcionando com pequenos problemas")
        else:
            print(f"   ❌ Sistema com problemas significativos")
        
        # Recomendações
        print(f"\n💡 Recomendações:")
        
        if not integrity_ok:
            print(f"   - Reconfigure o banco: python backend/shared_storage.py")
        
        if not network_ok:
            print(f"   - Verifique conectividade de rede")
            print(f"   - Considere usar pasta local se problemas persistirem")
        
        if performance_ok and performance_ok > 1.0:
            print(f"   - Performance lenta - considere otimizações de rede")
            print(f"   - Verifique se outros processos estão usando a rede")
        
        print(f"\n📞 Suporte:")
        print(f"   - Consulte logs em: {storage.shared_path / 'logs'}")
        print(f"   - Execute diagnóstico regularmente")
        print(f"   - Mantenha backups atualizados")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        return False


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n✅ Diagnóstico concluído com sucesso!")
        else:
            print(f"\n❌ Diagnóstico encontrou problemas")
        
        input("\nPressione Enter para sair...")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Diagnóstico cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")
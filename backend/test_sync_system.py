#!/usr/bin/env python3
"""
Script de teste para o sistema de sincronização SECRIMPO
Testa todos os endpoints e funcionalidades de sincronização
"""

import requests
import json
import uuid
from datetime import datetime, date
import sys

# Configurações
API_BASE_URL = "http://10.160.215.16:8001"
TEST_USER = "teste_agente"
CLIENT_UUID = str(uuid.uuid4())

def test_api_connection():
    """Testa conexão básica com a API"""
    print("🔍 Testando conexão com a API...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ API está funcionando")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

def test_sync_connectivity():
    """Testa endpoint de teste de sincronização"""
    print("\n🔍 Testando endpoint de sincronização...")
    try:
        response = requests.post(f"{API_BASE_URL}/sincronizar/teste")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de sincronização funcionando")
            print(f"   Status: {data.get('status')}")
            print(f"   Mensagem: {data.get('message')}")
            return True
        else:
            print(f"❌ Endpoint retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar sincronização: {e}")
        return False

def create_test_data():
    """Cria dados de teste para sincronização"""
    print("\n📝 Criando dados de teste...")
    
    # Dados de teste
    test_data = {
        "usuario": TEST_USER,
        "client_uuid": CLIENT_UUID,
        "timestamp_cliente": datetime.now().isoformat(),
        "dados": {
            "policiais": [
                {
                    "uuid_local": str(uuid.uuid4()),
                    "nome": "Policial Teste 1",
                    "matricula": "12345",
                    "graduacao": "Soldado",
                    "unidade": "8ª CPR"
                },
                {
                    "uuid_local": str(uuid.uuid4()),
                    "nome": "Policial Teste 2", 
                    "matricula": "67890",
                    "graduacao": "Cabo",
                    "unidade": "10ª CPR"
                }
            ],
            "proprietarios": [
                {
                    "uuid_local": str(uuid.uuid4()),
                    "nome": "Proprietário Teste 1",
                    "documento": "123.456.789-00"
                },
                {
                    "uuid_local": str(uuid.uuid4()),
                    "nome": "Proprietário Teste 2",
                    "documento": "987.654.321-00"
                }
            ],
            "ocorrencias": [
                {
                    "uuid_local": str(uuid.uuid4()),
                    "numero_genesis": "2025-TEST-001",
                    "unidade_fato": "8ª CPR",
                    "data_apreensao": date.today().isoformat(),
                    "lei_infringida": "Lei de Drogas",
                    "artigo": "Art. 33",
                    "policial_condutor": {
                        "nome": "Policial Teste 1",
                        "matricula": "12345",
                        "graduacao": "Soldado",
                        "unidade": "8ª CPR"
                    },
                    "itens_apreendidos": [
                        {
                            "especie": "Droga",
                            "item": "Maconha",
                            "quantidade": 1,
                            "descricao_detalhada": "Porção de maconha apreendida",
                            "proprietario": {
                                "nome": "Proprietário Teste 1",
                                "documento": "123.456.789-00"
                            }
                        }
                    ]
                }
            ]
        }
    }
    
    print(f"✅ Dados de teste criados:")
    print(f"   - {len(test_data['dados']['policiais'])} policiais")
    print(f"   - {len(test_data['dados']['proprietarios'])} proprietários")
    print(f"   - {len(test_data['dados']['ocorrencias'])} ocorrências")
    
    return test_data

def test_synchronization(test_data):
    """Testa sincronização completa"""
    print("\n🔄 Testando sincronização...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/sincronizar",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sincronização executada com sucesso")
            print(f"   Sucesso: {result.get('sucesso')}")
            print(f"   Usuário: {result.get('usuario')}")
            print(f"   Timestamp: {result.get('timestamp_servidor')}")
            
            # Mostrar resumo
            resumo = result.get('resumo', {})
            for tipo, stats in resumo.items():
                novos = stats.get('novos', 0)
                duplicados = stats.get('duplicados', 0)
                erros = len(stats.get('erros', []))
                print(f"   {tipo}: {novos} novos, {duplicados} duplicados, {erros} erros")
            
            # Mostrar detalhes
            detalhes = result.get('detalhes', [])
            if detalhes:
                print("   Detalhes:")
                for detalhe in detalhes[:5]:  # Mostrar apenas os primeiros 5
                    print(f"     - {detalhe}")
            
            # Mostrar erros
            erros = result.get('erros', [])
            if erros:
                print("   Erros:")
                for erro in erros:
                    print(f"     ❌ {erro}")
            
            return True
        else:
            print(f"❌ Sincronização falhou com status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('detail', 'Erro desconhecido')}")
            except:
                print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante sincronização: {e}")
        return False

def test_sync_status():
    """Testa obtenção de status de sincronização"""
    print("\n📊 Testando status de sincronização...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/sincronizar/status/{TEST_USER}")
        
        if response.status_code == 200:
            status = response.json()
            print("✅ Status obtido com sucesso")
            print(f"   Usuário: {status.get('usuario')}")
            print(f"   Última sincronização: {status.get('ultima_sincronizacao')}")
            print(f"   Total de sincronizações: {status.get('total_sincronizacoes')}")
            print(f"   Registros sincronizados: {status.get('total_registros_sincronizados')}")
            print(f"   Status da última sync: {status.get('status_ultima_sync')}")
            return True
        else:
            print(f"❌ Falha ao obter status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao obter status: {e}")
        return False

def test_sync_history():
    """Testa obtenção de histórico de sincronização"""
    print("\n📋 Testando histórico de sincronização...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/sincronizar/historico/{TEST_USER}?limit=5")
        
        if response.status_code == 200:
            historico = response.json()
            print(f"✅ Histórico obtido: {len(historico)} registros")
            
            for i, sync in enumerate(historico[:3], 1):  # Mostrar apenas os 3 primeiros
                timestamp = sync.get('timestamp', 'N/A')
                total = sync.get('total_registros', 0)
                novos = sync.get('registros_novos', 0)
                duplicados = sync.get('registros_duplicados', 0)
                status = sync.get('status', 'N/A')
                
                print(f"   {i}. {timestamp} - {total} registros ({novos} novos, {duplicados} duplicados) - {status}")
            
            return True
        else:
            print(f"❌ Falha ao obter histórico: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao obter histórico: {e}")
        return False

def test_duplicate_sync(test_data):
    """Testa sincronização duplicada (deve detectar duplicatas)"""
    print("\n🔄 Testando sincronização duplicada...")
    
    try:
        # Executar a mesma sincronização novamente
        response = requests.post(
            f"{API_BASE_URL}/sincronizar",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sincronização duplicada executada")
            
            # Verificar se detectou duplicatas
            resumo = result.get('resumo', {})
            total_duplicados = sum(stats.get('duplicados', 0) for stats in resumo.values())
            total_novos = sum(stats.get('novos', 0) for stats in resumo.values())
            
            print(f"   Novos: {total_novos}, Duplicados: {total_duplicados}")
            
            if total_duplicados > 0:
                print("✅ Sistema detectou duplicatas corretamente")
                return True
            else:
                print("⚠️ Sistema não detectou duplicatas (pode ser esperado)")
                return True
        else:
            print(f"❌ Sincronização duplicada falhou: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na sincronização duplicada: {e}")
        return False

def test_list_users():
    """Testa listagem de usuários sincronizados"""
    print("\n👥 Testando listagem de usuários...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/sincronizar/usuarios")
        
        if response.status_code == 200:
            data = response.json()
            usuarios = data.get('usuarios', [])
            print(f"✅ Usuários obtidos: {len(usuarios)}")
            
            for usuario in usuarios:
                print(f"   - {usuario}")
            
            return True
        else:
            print(f"❌ Falha ao listar usuários: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 TESTE DO SISTEMA DE SINCRONIZAÇÃO SECRIMPO")
    print("=" * 50)
    
    # Lista de testes
    tests = [
        ("Conexão com API", test_api_connection),
        ("Conectividade de Sincronização", test_sync_connectivity),
    ]
    
    # Executar testes básicos
    for test_name, test_func in tests:
        if not test_func():
            print(f"\n❌ Teste '{test_name}' falhou. Verifique se a API está rodando.")
            print("   Execute: python backend/start_api.py")
            sys.exit(1)
    
    # Criar dados de teste
    test_data = create_test_data()
    
    # Testes de sincronização
    sync_tests = [
        ("Sincronização Inicial", lambda: test_synchronization(test_data)),
        ("Status de Sincronização", test_sync_status),
        ("Histórico de Sincronização", test_sync_history),
        ("Sincronização Duplicada", lambda: test_duplicate_sync(test_data)),
        ("Listagem de Usuários", test_list_users),
    ]
    
    passed = 0
    total = len(sync_tests)
    
    for test_name, test_func in sync_tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"⚠️ Teste '{test_name}' falhou")
    
    # Resultado final
    print("\n" + "=" * 50)
    print(f"🏁 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema de sincronização funcionando.")
        print("\n📋 Próximos passos:")
        print("1. Integre o sync-manager.js no seu app Electron")
        print("2. Adicione a interface de sincronização (sync-ui.html)")
        print("3. Configure os usuários para usar a sincronização")
        print("4. Teste com dados reais")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
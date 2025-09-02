#!/usr/bin/env python3
"""
Teste básico do sistema de sincronização SECRIMPO
Usa apenas bibliotecas padrão do Python
"""

import urllib.request
import urllib.parse
import json
import uuid
from datetime import datetime, date

# Configurações
API_BASE_URL = "http://10.160.215.16:8001"
TEST_USER = "teste_agente"
CLIENT_UUID = str(uuid.uuid4())

def make_request(url, method="GET", data=None):
    """Faz uma requisição HTTP usando urllib"""
    try:
        if data:
            # POST request
            data_json = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_json, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            # GET request
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = response.read().decode('utf-8')
            return True, json.loads(response_data) if response_data else {}
            
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_data)
            return False, error_json
        except:
            return False, {"error": f"HTTP {e.code}: {error_data}"}
    except Exception as e:
        return False, {"error": str(e)}

def test_api_connection():
    """Testa conexão básica com a API"""
    print("🔍 Testando conexão com a API...")
    success, data = make_request(f"{API_BASE_URL}/")
    
    if success:
        print("✅ API está funcionando")
        print(f"   Mensagem: {data.get('message', 'N/A')}")
        print(f"   Versão: {data.get('version', 'N/A')}")
        return True
    else:
        print(f"❌ Erro na API: {data.get('error', 'Erro desconhecido')}")
        return False

def test_sync_connectivity():
    """Testa endpoint de teste de sincronização"""
    print("\n🔍 Testando endpoint de sincronização...")
    success, data = make_request(f"{API_BASE_URL}/sincronizar/teste", "POST")
    
    if success:
        print("✅ Endpoint de sincronização funcionando")
        print(f"   Status: {data.get('status', 'N/A')}")
        print(f"   Mensagem: {data.get('message', 'N/A')}")
        return True
    else:
        print(f"❌ Erro no endpoint: {data.get('error', 'Erro desconhecido')}")
        return False

def create_test_data():
    """Cria dados de teste para sincronização"""
    print("\n📝 Criando dados de teste...")
    
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
    
    total_registros = (len(test_data['dados']['policiais']) + 
                      len(test_data['dados']['proprietarios']) + 
                      len(test_data['dados']['ocorrencias']))
    
    print(f"✅ Dados de teste criados:")
    print(f"   - {len(test_data['dados']['policiais'])} policiais")
    print(f"   - {len(test_data['dados']['proprietarios'])} proprietários")
    print(f"   - {len(test_data['dados']['ocorrencias'])} ocorrências")
    print(f"   - Total: {total_registros} registros")
    
    return test_data

def test_synchronization(test_data):
    """Testa sincronização completa"""
    print("\n🔄 Testando sincronização...")
    
    success, data = make_request(f"{API_BASE_URL}/sincronizar", "POST", test_data)
    
    if success:
        print("✅ Sincronização executada com sucesso")
        print(f"   Sucesso: {data.get('sucesso', False)}")
        print(f"   Usuário: {data.get('usuario', 'N/A')}")
        print(f"   Timestamp: {data.get('timestamp_servidor', 'N/A')}")
        
        # Mostrar resumo
        resumo = data.get('resumo', {})
        for tipo, stats in resumo.items():
            novos = stats.get('novos', 0)
            duplicados = stats.get('duplicados', 0)
            print(f"   {tipo}: {novos} novos, {duplicados} duplicados")
        
        # Mostrar detalhes (primeiros 3)
        detalhes = data.get('detalhes', [])
        if detalhes:
            print("   Detalhes:")
            for detalhe in detalhes[:3]:
                print(f"     - {detalhe}")
            if len(detalhes) > 3:
                print(f"     ... e mais {len(detalhes) - 3} itens")
        
        # Mostrar erros
        erros = data.get('erros', [])
        if erros:
            print("   Erros:")
            for erro in erros[:3]:
                print(f"     ❌ {erro}")
            if len(erros) > 3:
                print(f"     ... e mais {len(erros) - 3} erros")
        
        return True
    else:
        print(f"❌ Sincronização falhou: {data.get('error', 'Erro desconhecido')}")
        return False

def test_sync_status():
    """Testa obtenção de status de sincronização"""
    print("\n📊 Testando status de sincronização...")
    
    success, data = make_request(f"{API_BASE_URL}/sincronizar/status/{TEST_USER}")
    
    if success:
        print("✅ Status obtido com sucesso")
        print(f"   Usuário: {data.get('usuario', 'N/A')}")
        print(f"   Última sincronização: {data.get('ultima_sincronizacao', 'Nunca')}")
        print(f"   Total de sincronizações: {data.get('total_sincronizacoes', 0)}")
        print(f"   Registros sincronizados: {data.get('total_registros_sincronizados', 0)}")
        print(f"   Status da última sync: {data.get('status_ultima_sync', 'N/A')}")
        return True
    else:
        print(f"❌ Falha ao obter status: {data.get('error', 'Erro desconhecido')}")
        return False

def test_sync_history():
    """Testa obtenção de histórico de sincronização"""
    print("\n📋 Testando histórico de sincronização...")
    
    success, data = make_request(f"{API_BASE_URL}/sincronizar/historico/{TEST_USER}?limit=5")
    
    if success:
        if isinstance(data, list):
            print(f"✅ Histórico obtido: {len(data)} registros")
            
            for i, sync in enumerate(data[:3], 1):
                timestamp = sync.get('timestamp', 'N/A')
                total = sync.get('total_registros', 0)
                novos = sync.get('registros_novos', 0)
                duplicados = sync.get('registros_duplicados', 0)
                status = sync.get('status', 'N/A')
                
                print(f"   {i}. {timestamp} - {total} registros ({novos} novos, {duplicados} duplicados) - {status}")
            
            if len(data) > 3:
                print(f"   ... e mais {len(data) - 3} registros")
        else:
            print("✅ Histórico obtido (formato inesperado)")
        
        return True
    else:
        print(f"❌ Falha ao obter histórico: {data.get('error', 'Erro desconhecido')}")
        return False

def test_list_users():
    """Testa listagem de usuários sincronizados"""
    print("\n👥 Testando listagem de usuários...")
    
    success, data = make_request(f"{API_BASE_URL}/sincronizar/usuarios")
    
    if success:
        usuarios = data.get('usuarios', [])
        print(f"✅ Usuários obtidos: {len(usuarios)}")
        
        for usuario in usuarios:
            print(f"   - {usuario}")
        
        return True
    else:
        print(f"❌ Falha ao listar usuários: {data.get('error', 'Erro desconhecido')}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 TESTE BÁSICO DO SISTEMA DE SINCRONIZAÇÃO SECRIMPO")
    print("=" * 60)
    print(f"🌐 Servidor: {API_BASE_URL}")
    print(f"👤 Usuário de teste: {TEST_USER}")
    print()
    
    # Testes básicos
    basic_tests = [
        ("Conexão com API", test_api_connection),
        ("Conectividade de Sincronização", test_sync_connectivity),
    ]
    
    for test_name, test_func in basic_tests:
        if not test_func():
            print(f"\n❌ Teste '{test_name}' falhou.")
            print("   Verifique se o servidor está rodando:")
            print("   cd backend")
            print("   python basic_sync_server.py")
            return False
    
    # Criar dados de teste
    test_data = create_test_data()
    
    # Testes de sincronização
    sync_tests = [
        ("Sincronização Inicial", lambda: test_synchronization(test_data)),
        ("Status de Sincronização", test_sync_status),
        ("Histórico de Sincronização", test_sync_history),
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
    print("\n" + "=" * 60)
    print(f"🏁 RESULTADO FINAL: {passed}/{total} testes de sincronização passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema de sincronização funcionando.")
        print("\n📋 Próximos passos:")
        print("1. Integre o sync-manager.js no seu app Electron")
        print("2. Abra frontend/src/sync-ui.html para testar a interface")
        print("3. Configure outros usuários com o mesmo IP do servidor")
        print(f"4. Compartilhe a URL: {API_BASE_URL}")
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        print("   Certifique-se de que o servidor está rodando.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        input("\n✅ Pressione Enter para sair...")
    except KeyboardInterrupt:
        print("\n\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")
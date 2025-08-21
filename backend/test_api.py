#!/usr/bin/env python3
"""
Script para visualizar dados existentes na API SECRIMPO
"""
import requests
import json
from datetime import date

API_BASE = "http://127.0.0.1:8000"

def format_table(data, title):
    """Formata dados em tabela para exibição"""
    if not data:
        print(f"   📭 Nenhum {title.lower()} encontrado")
        return
    
    print(f"   📊 Total: {len(data)} {title.lower()}(s)")
    for i, item in enumerate(data, 1):
        print(f"   {i:2d}. {format_item(item)}")

def format_item(item):
    """Formata um item individual"""
    if 'nome' in item and 'matricula' in item:
        # Policial
        return f"{item['nome']} (Mat: {item['matricula']}) - {item['graduacao']} - {item['unidade']}"
    elif 'nome' in item and 'documento' in item:
        # Proprietário
        return f"{item['nome']} (Doc: {item['documento']})"
    elif 'numero_genesis' in item:
        # Ocorrência
        return f"Genesis: {item['numero_genesis']} | {item['unidade_fato']} | {item['data_apreensao']} | {item['lei_infringida']}"
    elif 'especie' in item:
        # Item apreendido
        return f"{item['especie']} - {item['item']} (Qtd: {item['quantidade']}) - {item['descricao_detalhada'][:50]}..."
    else:
        return str(item)

def view_database():
    """Visualiza todos os dados existentes no banco"""
    print("🔍 VISUALIZANDO DADOS EXISTENTES NO BANCO SECRIMPO")
    print("=" * 60)
    
    try:
        # Health check
        print("\n🏥 Verificando conexão com a API...")
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            api_info = response.json()
            print(f"   ✅ {api_info['message']} (v{api_info.get('version', 'N/A')})")
        else:
            print(f"   ❌ Erro na conexão: {response.status_code}")
            return
        
        # Estatísticas gerais
        print("\n📈 ESTATÍSTICAS GERAIS")
        print("-" * 30)
        response = requests.get(f"{API_BASE}/estatisticas/")
        if response.status_code == 200:
            stats = response.json()
            print(f"   👮 Policiais: {stats['total_policiais']}")
            print(f"   👤 Proprietários: {stats['total_proprietarios']}")
            print(f"   📋 Ocorrências: {stats['total_ocorrencias']}")
            print(f"   📦 Itens Apreendidos: {stats['total_itens']}")
        
        # Listar policiais
        print("\n👮 POLICIAIS CADASTRADOS")
        print("-" * 30)
        response = requests.get(f"{API_BASE}/policiais/")
        if response.status_code == 200:
            policiais = response.json()
            format_table(policiais, "Policial")
        else:
            print(f"   ❌ Erro ao buscar policiais: {response.status_code}")
        
        # Listar proprietários
        print("\n👤 PROPRIETÁRIOS CADASTRADOS")
        print("-" * 30)
        response = requests.get(f"{API_BASE}/proprietarios/")
        if response.status_code == 200:
            proprietarios = response.json()
            format_table(proprietarios, "Proprietário")
        else:
            print(f"   ❌ Erro ao buscar proprietários: {response.status_code}")
        
        # Listar ocorrências
        print("\n📋 OCORRÊNCIAS REGISTRADAS")
        print("-" * 30)
        response = requests.get(f"{API_BASE}/ocorrencias/")
        if response.status_code == 200:
            ocorrencias = response.json()
            format_table(ocorrencias, "Ocorrência")
            
            # Para cada ocorrência, listar itens
            if ocorrencias:
                print("\n📦 ITENS POR OCORRÊNCIA")
                print("-" * 30)
                for ocorrencia in ocorrencias:
                    print(f"\n   🔸 Ocorrência Genesis: {ocorrencia['numero_genesis']}")
                    response = requests.get(f"{API_BASE}/itens/ocorrencia/{ocorrencia['id']}")
                    if response.status_code == 200:
                        itens = response.json()
                        if itens:
                            for j, item in enumerate(itens, 1):
                                print(f"      {j}. {format_item(item)}")
                        else:
                            print("      📭 Nenhum item apreendido")
        else:
            print(f"   ❌ Erro ao buscar ocorrências: {response.status_code}")
        
        # Listar todos os itens
        print("\n📦 TODOS OS ITENS APREENDIDOS")
        print("-" * 30)
        response = requests.get(f"{API_BASE}/itens/")
        if response.status_code == 200:
            itens = response.json()
            format_table(itens, "Item")
        else:
            print(f"   ❌ Erro ao buscar itens: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("✅ Visualização concluída com sucesso!")
        print("💡 Para adicionar novos dados, use o frontend Electron ou faça requisições POST para a API")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar à API.")
        print("🔧 Certifique-se de que o servidor está rodando:")
        print("   cd backend && python start_api.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_endpoints():
    """Testa se todos os endpoints estão respondendo"""
    print("\n🧪 TESTANDO ENDPOINTS DA API")
    print("-" * 30)
    
    endpoints = [
        ("GET", "/", "Health Check"),
        ("GET", "/policiais/", "Listar Policiais"),
        ("GET", "/proprietarios/", "Listar Proprietários"),
        ("GET", "/ocorrencias/", "Listar Ocorrências"),
        ("GET", "/itens/", "Listar Itens"),
        ("GET", "/estatisticas/", "Estatísticas")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {description}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description}: Erro - {e}")

if __name__ == "__main__":
    view_database()
    test_endpoints()
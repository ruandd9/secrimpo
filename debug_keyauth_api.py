#!/usr/bin/env python3
"""
Script para debugar a conexão com a API KeyAuth
"""

import requests
import json

def test_keyauth_api():
    """Testa a conexão com a API KeyAuth"""
    
    owner_id = "eqVjoVksfB"
    secret = "61448643819ae5b00418dcfe9d171662a62db6d16cad37f8bc7ce57420efa1c4"
    
    print("🔍 Testando Conexão com API KeyAuth")
    print("=" * 40)
    
    # Teste 1: Verificar se a API responde
    print("\n1. Testando URL base da API...")
    try:
        response = requests.get("https://keyauth.win/api/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 2: Testar endpoint de assinaturas
    print("\n2. Testando endpoint de assinaturas...")
    data = {
        "type": "fetchallsubs",
        "format": "JSON",
        "ownerid": owner_id,
        "secret": secret
    }
    
    try:
        response = requests.post("https://keyauth.win/api/seller/", data=data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Resposta bruta: {response.text}")
        
        if response.text:
            try:
                json_response = response.json()
                print(f"   JSON válido: {json_response}")
            except json.JSONDecodeError:
                print("   ❌ Resposta não é JSON válido")
        
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 3: Testar com diferentes URLs
    print("\n3. Testando URLs alternativas...")
    
    urls_alternativas = [
        "https://keyauth.win/api/seller/",
        "https://keyauth.cc/api/seller/",
        "https://keyauth.win/api/1.2/",
    ]
    
    for url in urls_alternativas:
        print(f"\n   Testando: {url}")
        try:
            response = requests.post(url, data=data, timeout=5)
            print(f"   Status: {response.status_code}")
            if response.text:
                print(f"   Resposta: {response.text[:200]}...")
        except Exception as e:
            print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_keyauth_api()
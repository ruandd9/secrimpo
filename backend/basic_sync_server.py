#!/usr/bin/env python3
"""
Servidor Básico de Sincronização SECRIMPO
Usa apenas bibliotecas padrão do Python (http.server, sqlite3, json)
"""

import http.server
import socketserver
import json
import sqlite3
import hashlib
import urllib.parse
from datetime import datetime
import uuid
import os
from pathlib import Path

# Configurações
PORT = 8001  # Mudando para porta 8001
DATABASE_PATH = "sync_database.db"

class SyncDatabase:
    """Gerenciador de banco de dados para sincronização"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de policiais
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                matricula TEXT UNIQUE NOT NULL,
                graduacao TEXT NOT NULL,
                unidade TEXT NOT NULL,
                uuid_local TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de proprietários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proprietario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT NOT NULL,
                uuid_local TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de ocorrências
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ocorrencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_genesis TEXT NOT NULL,
                unidade_fato TEXT NOT NULL,
                data_apreensao DATE NOT NULL,
                lei_infringida TEXT NOT NULL,
                artigo TEXT NOT NULL,
                policial_condutor_id INTEGER,
                uuid_local TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de logs de sincronização
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_registros INTEGER DEFAULT 0,
                registros_novos INTEGER DEFAULT 0,
                registros_duplicados INTEGER DEFAULT 0,
                status TEXT DEFAULT 'sucesso',
                detalhes TEXT,
                client_uuid TEXT
            )
        ''')
        
        # Tabela de controle de sincronização
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registro_sincronizado (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                tipo_registro TEXT NOT NULL,
                uuid_local TEXT NOT NULL,
                id_central INTEGER NOT NULL,
                timestamp_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                hash_dados TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Banco de dados inicializado: {self.db_path}")
    
    def execute_query(self, query: str, params: tuple = ()):
        """Executa uma query"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                results = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                results = [{"id": cursor.lastrowid, "changes": cursor.rowcount}]
            return results
        finally:
            conn.close()
    
    def insert_or_get_policial(self, dados):
        """Insere ou obtém policial"""
        existing = self.execute_query(
            "SELECT id FROM policial WHERE matricula = ?",
            (dados["matricula"],)
        )
        
        if existing:
            return existing[0]["id"]
        
        result = self.execute_query(
            "INSERT INTO policial (nome, matricula, graduacao, unidade, uuid_local) VALUES (?, ?, ?, ?, ?)",
            (dados["nome"], dados["matricula"], dados["graduacao"], dados["unidade"], dados.get("uuid_local"))
        )
        
        return result[0]["id"]
    
    def insert_or_get_proprietario(self, dados):
        """Insere ou obtém proprietário"""
        existing = self.execute_query(
            "SELECT id FROM proprietario WHERE documento = ?",
            (dados["documento"],)
        )
        
        if existing:
            return existing[0]["id"]
        
        result = self.execute_query(
            "INSERT INTO proprietario (nome, documento, uuid_local) VALUES (?, ?, ?)",
            (dados["nome"], dados["documento"], dados.get("uuid_local"))
        )
        
        return result[0]["id"]
    
    def insert_ocorrencia(self, dados, policial_id):
        """Insere ocorrência"""
        result = self.execute_query(
            """INSERT INTO ocorrencia 
               (numero_genesis, unidade_fato, data_apreensao, lei_infringida, artigo, policial_condutor_id, uuid_local) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (dados["numero_genesis"], dados["unidade_fato"], dados["data_apreensao"], 
             dados["lei_infringida"], dados["artigo"], policial_id, dados.get("uuid_local"))
        )
        
        return result[0]["id"]
    
    def is_synced(self, usuario, tipo, uuid_local):
        """Verifica se já foi sincronizado"""
        result = self.execute_query(
            "SELECT id FROM registro_sincronizado WHERE usuario = ? AND tipo_registro = ? AND uuid_local = ?",
            (usuario, tipo, uuid_local)
        )
        return len(result) > 0
    
    def mark_synced(self, usuario, tipo, uuid_local, id_central, hash_dados):
        """Marca como sincronizado"""
        self.execute_query(
            "INSERT INTO registro_sincronizado (usuario, tipo_registro, uuid_local, id_central, hash_dados) VALUES (?, ?, ?, ?, ?)",
            (usuario, tipo, uuid_local, id_central, hash_dados)
        )
    
    def log_sync(self, usuario, client_uuid, total, novos, duplicados, status, detalhes):
        """Log de sincronização"""
        result = self.execute_query(
            "INSERT INTO sync_log (usuario, total_registros, registros_novos, registros_duplicados, status, detalhes, client_uuid) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (usuario, total, novos, duplicados, status, detalhes, client_uuid)
        )
        return result[0]["id"]

class SyncRequestHandler(http.server.BaseHTTPRequestHandler):
    """Handler para requisições de sincronização"""
    
    def __init__(self, *args, **kwargs):
        self.db = SyncDatabase(DATABASE_PATH)
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """Envia headers CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_json_response(self, data, status_code=200):
        """Envia resposta JSON"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False, default=str)
        self.wfile.write(response.encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        path = self.path.split('?')[0]  # Remove query parameters
        
        if path == '/':
            self.send_json_response({
                "message": "SECRIMPO Sync Server funcionando!",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            })
        
        elif path.startswith('/sincronizar/status/'):
            usuario = path.split('/')[-1]
            self.handle_get_status(usuario)
        
        elif path.startswith('/sincronizar/historico/'):
            usuario = path.split('/')[-1]
            self.handle_get_history(usuario)
        
        elif path == '/sincronizar/usuarios':
            self.handle_list_users()
        
        elif path == '/estatisticas':
            self.handle_get_stats()
        
        else:
            self.send_json_response({"error": "Endpoint não encontrado"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        path = self.path
        
        if path == '/sincronizar/teste':
            self.send_json_response({
                "status": "ok",
                "message": "Servidor de sincronização funcionando",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            })
        
        elif path == '/sincronizar':
            self.handle_sync()
        
        else:
            self.send_json_response({"error": "Endpoint não encontrado"}, 404)
    
    def handle_sync(self):
        """Handle sincronização"""
        try:
            # Ler dados da requisição
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Validar campos obrigatórios
            usuario = request_data.get("usuario")
            client_uuid = request_data.get("client_uuid")
            dados = request_data.get("dados", {})
            
            if not usuario:
                self.send_json_response({"error": "Campo 'usuario' é obrigatório"}, 400)
                return
            
            if not client_uuid:
                self.send_json_response({"error": "Campo 'client_uuid' é obrigatório"}, 400)
                return
            
            print(f"🔄 Sincronizando dados para usuário: {usuario}")
            
            resultado = {
                "sucesso": True,
                "usuario": usuario,
                "timestamp_servidor": datetime.now().isoformat(),
                "resumo": {},
                "detalhes": [],
                "erros": []
            }
            
            total_novos = 0
            total_duplicados = 0
            
            # Processar policiais
            if "policiais" in dados:
                novos, duplicados, detalhes, erros = self.process_policiais(usuario, dados["policiais"])
                resultado["resumo"]["policiais"] = {"novos": novos, "duplicados": duplicados}
                resultado["detalhes"].extend(detalhes)
                resultado["erros"].extend(erros)
                total_novos += novos
                total_duplicados += duplicados
            
            # Processar proprietários
            if "proprietarios" in dados:
                novos, duplicados, detalhes, erros = self.process_proprietarios(usuario, dados["proprietarios"])
                resultado["resumo"]["proprietarios"] = {"novos": novos, "duplicados": duplicados}
                resultado["detalhes"].extend(detalhes)
                resultado["erros"].extend(erros)
                total_novos += novos
                total_duplicados += duplicados
            
            # Processar ocorrências
            if "ocorrencias" in dados:
                novos, duplicados, detalhes, erros = self.process_ocorrencias(usuario, dados["ocorrencias"])
                resultado["resumo"]["ocorrencias"] = {"novos": novos, "duplicados": duplicados}
                resultado["detalhes"].extend(detalhes)
                resultado["erros"].extend(erros)
                total_novos += novos
                total_duplicados += duplicados
            
            # Log da sincronização
            status = "sucesso" if not resultado["erros"] else "parcial"
            sync_id = self.db.log_sync(usuario, client_uuid, total_novos + total_duplicados, 
                                     total_novos, total_duplicados, status, json.dumps(resultado["resumo"]))
            resultado["sync_id"] = sync_id
            
            print(f"✅ Sincronização concluída: {total_novos} novos, {total_duplicados} duplicados")
            
            self.send_json_response(resultado)
            
        except Exception as e:
            print(f"❌ Erro durante sincronização: {str(e)}")
            self.send_json_response({"error": f"Erro interno: {str(e)}"}, 500)
    
    def process_policiais(self, usuario, policiais):
        """Processa lista de policiais"""
        novos = 0
        duplicados = 0
        detalhes = []
        erros = []
        
        for policial_data in policiais:
            try:
                uuid_local = policial_data.get("uuid_local")
                if not uuid_local:
                    erros.append("Policial sem UUID local")
                    continue
                
                if self.db.is_synced(usuario, "policial", uuid_local):
                    duplicados += 1
                    continue
                
                policial_id = self.db.insert_or_get_policial(policial_data)
                hash_dados = hashlib.md5(json.dumps(policial_data, sort_keys=True).encode()).hexdigest()
                self.db.mark_synced(usuario, "policial", uuid_local, policial_id, hash_dados)
                
                novos += 1
                detalhes.append(f"Policial {policial_data['matricula']} sincronizado")
                
            except Exception as e:
                erros.append(f"Erro ao sincronizar policial: {str(e)}")
        
        return novos, duplicados, detalhes, erros
    
    def process_proprietarios(self, usuario, proprietarios):
        """Processa lista de proprietários"""
        novos = 0
        duplicados = 0
        detalhes = []
        erros = []
        
        for prop_data in proprietarios:
            try:
                uuid_local = prop_data.get("uuid_local")
                if not uuid_local:
                    erros.append("Proprietário sem UUID local")
                    continue
                
                if self.db.is_synced(usuario, "proprietario", uuid_local):
                    duplicados += 1
                    continue
                
                prop_id = self.db.insert_or_get_proprietario(prop_data)
                hash_dados = hashlib.md5(json.dumps(prop_data, sort_keys=True).encode()).hexdigest()
                self.db.mark_synced(usuario, "proprietario", uuid_local, prop_id, hash_dados)
                
                novos += 1
                detalhes.append(f"Proprietário {prop_data['documento']} sincronizado")
                
            except Exception as e:
                erros.append(f"Erro ao sincronizar proprietário: {str(e)}")
        
        return novos, duplicados, detalhes, erros
    
    def process_ocorrencias(self, usuario, ocorrencias):
        """Processa lista de ocorrências"""
        novos = 0
        duplicados = 0
        detalhes = []
        erros = []
        
        for ocor_data in ocorrencias:
            try:
                uuid_local = ocor_data.get("uuid_local")
                if not uuid_local:
                    erros.append("Ocorrência sem UUID local")
                    continue
                
                if self.db.is_synced(usuario, "ocorrencia", uuid_local):
                    duplicados += 1
                    continue
                
                # Processar policial condutor
                policial_data = ocor_data.get("policial_condutor", {})
                policial_id = self.db.insert_or_get_policial(policial_data)
                
                # Inserir ocorrência
                ocorrencia_id = self.db.insert_ocorrencia(ocor_data, policial_id)
                
                hash_dados = hashlib.md5(json.dumps(ocor_data, sort_keys=True).encode()).hexdigest()
                self.db.mark_synced(usuario, "ocorrencia", uuid_local, ocorrencia_id, hash_dados)
                
                novos += 1
                detalhes.append(f"Ocorrência {ocor_data['numero_genesis']} sincronizada")
                
            except Exception as e:
                erros.append(f"Erro ao sincronizar ocorrência: {str(e)}")
        
        return novos, duplicados, detalhes, erros
    
    def handle_get_status(self, usuario):
        """Handle status request"""
        try:
            last_sync = self.db.execute_query(
                "SELECT * FROM sync_log WHERE usuario = ? ORDER BY timestamp DESC LIMIT 1",
                (usuario,)
            )
            
            total_syncs = self.db.execute_query(
                "SELECT COUNT(*) as count FROM sync_log WHERE usuario = ?",
                (usuario,)
            )[0]["count"]
            
            total_records = self.db.execute_query(
                "SELECT COUNT(*) as count FROM registro_sincronizado WHERE usuario = ?",
                (usuario,)
            )[0]["count"]
            
            self.send_json_response({
                "usuario": usuario,
                "ultima_sincronizacao": last_sync[0]["timestamp"] if last_sync else None,
                "total_sincronizacoes": total_syncs,
                "total_registros_sincronizados": total_records,
                "status_ultima_sync": last_sync[0]["status"] if last_sync else "nunca_sincronizado"
            })
            
        except Exception as e:
            self.send_json_response({"error": f"Erro ao obter status: {str(e)}"}, 500)
    
    def handle_get_history(self, usuario):
        """Handle history request"""
        try:
            historico = self.db.execute_query(
                "SELECT * FROM sync_log WHERE usuario = ? ORDER BY timestamp DESC LIMIT 10",
                (usuario,)
            )
            
            self.send_json_response(historico)
            
        except Exception as e:
            self.send_json_response({"error": f"Erro ao obter histórico: {str(e)}"}, 500)
    
    def handle_list_users(self):
        """Handle list users request"""
        try:
            usuarios = self.db.execute_query("SELECT DISTINCT usuario FROM sync_log")
            self.send_json_response({"usuarios": [u["usuario"] for u in usuarios]})
            
        except Exception as e:
            self.send_json_response({"error": f"Erro ao listar usuários: {str(e)}"}, 500)
    
    def handle_get_stats(self):
        """Handle statistics request"""
        try:
            stats = {}
            
            for table in ["policial", "proprietario", "ocorrencia"]:
                count = self.db.execute_query(f"SELECT COUNT(*) as count FROM {table}")[0]["count"]
                stats[f"total_{table}s"] = count
            
            self.send_json_response(stats)
            
        except Exception as e:
            self.send_json_response({"error": f"Erro ao obter estatísticas: {str(e)}"}, 500)
    
    def log_message(self, format, *args):
        """Suprimir logs desnecessários"""
        pass

def main():
    """Função principal"""
    print("🚀 Iniciando SECRIMPO Sync Server...")
    print(f"📊 Banco de dados: {DATABASE_PATH}")
    print(f"🌐 Servidor: http://127.0.0.1:{PORT}")
    print("📋 Endpoints disponíveis:")
    print("   POST /sincronizar - Sincronizar dados")
    print("   POST /sincronizar/teste - Testar conectividade")
    print("   GET /sincronizar/status/{usuario} - Status do usuário")
    print("   GET /sincronizar/historico/{usuario} - Histórico do usuário")
    print("   GET /sincronizar/usuarios - Listar usuários")
    print("   GET /estatisticas - Estatísticas gerais")
    print()
    
    # Inicializar banco
    db = SyncDatabase(DATABASE_PATH)
    
    # Configurar IP do servidor
    # Para aceitar conexões de qualquer IP, use "0.0.0.0"
    # Para aceitar apenas local, use "127.0.0.1"
    SERVER_HOST = "0.0.0.0"  # Permite conexões externas
    
    # Iniciar servidor
    with socketserver.TCPServer((SERVER_HOST, PORT), SyncRequestHandler) as httpd:
        print(f"✅ Servidor rodando na porta {PORT}")
        print("Pressione Ctrl+C para parar")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n⏹️ Servidor interrompido pelo usuário")

if __name__ == "__main__":
    main()
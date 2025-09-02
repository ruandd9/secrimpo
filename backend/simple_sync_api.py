#!/usr/bin/env python3
"""
API Simplificada de Sincronização SECRIMPO
Versão standalone que não depende de imports complexos
"""

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    import json
    import sqlite3
    import hashlib
    from datetime import datetime
    from typing import Dict, List, Any, Optional
    import uuid
    import os
    from pathlib import Path
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Execute: pip install fastapi uvicorn")
    exit(1)

# Configurações
DATABASE_PATH = "sync_database.db"
API_HOST = "127.0.0.1"
API_PORT = 8000

# Criar aplicação FastAPI
app = FastAPI(
    title="SECRIMPO Sync API",
    description="API de sincronização para SECRIMPO",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatabaseManager:
    """Gerenciador simples de banco de dados"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (policial_condutor_id) REFERENCES policial (id)
            )
        ''')
        
        # Tabela de itens apreendidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS item_apreendido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                especie TEXT NOT NULL,
                item TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                descricao_detalhada TEXT NOT NULL,
                ocorrencia_id INTEGER NOT NULL,
                proprietario_id INTEGER NOT NULL,
                policial_id INTEGER NOT NULL,
                uuid_local TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ocorrencia_id) REFERENCES ocorrencia (id),
                FOREIGN KEY (proprietario_id) REFERENCES proprietario (id),
                FOREIGN KEY (policial_id) REFERENCES policial (id)
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
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Executa uma query e retorna os resultados"""
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
    
    def insert_or_get_policial(self, dados: Dict) -> int:
        """Insere ou obtém ID de um policial"""
        # Verificar se já existe
        existing = self.execute_query(
            "SELECT id FROM policial WHERE matricula = ?",
            (dados["matricula"],)
        )
        
        if existing:
            return existing[0]["id"]
        
        # Inserir novo
        result = self.execute_query(
            "INSERT INTO policial (nome, matricula, graduacao, unidade, uuid_local) VALUES (?, ?, ?, ?, ?)",
            (dados["nome"], dados["matricula"], dados["graduacao"], dados["unidade"], dados.get("uuid_local"))
        )
        
        return result[0]["id"]
    
    def insert_or_get_proprietario(self, dados: Dict) -> int:
        """Insere ou obtém ID de um proprietário"""
        # Verificar se já existe
        existing = self.execute_query(
            "SELECT id FROM proprietario WHERE documento = ?",
            (dados["documento"],)
        )
        
        if existing:
            return existing[0]["id"]
        
        # Inserir novo
        result = self.execute_query(
            "INSERT INTO proprietario (nome, documento, uuid_local) VALUES (?, ?, ?)",
            (dados["nome"], dados["documento"], dados.get("uuid_local"))
        )
        
        return result[0]["id"]
    
    def insert_ocorrencia(self, dados: Dict, policial_id: int) -> int:
        """Insere uma nova ocorrência"""
        result = self.execute_query(
            """INSERT INTO ocorrencia 
               (numero_genesis, unidade_fato, data_apreensao, lei_infringida, artigo, policial_condutor_id, uuid_local) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (dados["numero_genesis"], dados["unidade_fato"], dados["data_apreensao"], 
             dados["lei_infringida"], dados["artigo"], policial_id, dados.get("uuid_local"))
        )
        
        return result[0]["id"]
    
    def insert_item_apreendido(self, dados: Dict, ocorrencia_id: int, proprietario_id: int, policial_id: int):
        """Insere um item apreendido"""
        self.execute_query(
            """INSERT INTO item_apreendido 
               (especie, item, quantidade, descricao_detalhada, ocorrencia_id, proprietario_id, policial_id, uuid_local) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (dados["especie"], dados["item"], dados["quantidade"], dados["descricao_detalhada"],
             ocorrencia_id, proprietario_id, policial_id, dados.get("uuid_local"))
        )
    
    def log_sync(self, usuario: str, client_uuid: str, total: int, novos: int, duplicados: int, status: str, detalhes: str) -> int:
        """Registra log de sincronização"""
        result = self.execute_query(
            "INSERT INTO sync_log (usuario, total_registros, registros_novos, registros_duplicados, status, detalhes, client_uuid) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (usuario, total, novos, duplicados, status, detalhes, client_uuid)
        )
        return result[0]["id"]
    
    def mark_synced(self, usuario: str, tipo: str, uuid_local: str, id_central: int, hash_dados: str):
        """Marca um registro como sincronizado"""
        self.execute_query(
            "INSERT INTO registro_sincronizado (usuario, tipo_registro, uuid_local, id_central, hash_dados) VALUES (?, ?, ?, ?, ?)",
            (usuario, tipo, uuid_local, id_central, hash_dados)
        )
    
    def is_synced(self, usuario: str, tipo: str, uuid_local: str) -> bool:
        """Verifica se um registro já foi sincronizado"""
        result = self.execute_query(
            "SELECT id FROM registro_sincronizado WHERE usuario = ? AND tipo_registro = ? AND uuid_local = ?",
            (usuario, tipo, uuid_local)
        )
        return len(result) > 0

# Instância global do banco
db = DatabaseManager(DATABASE_PATH)

def calculate_hash(data: Dict) -> str:
    """Calcula hash dos dados"""
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "SECRIMPO Sync API funcionando!",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/sincronizar/teste")
async def test_sync():
    """Teste de conectividade"""
    return {
        "status": "ok",
        "message": "Servidor de sincronização funcionando",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/sincronizar")
async def sincronizar_dados(request: Dict[str, Any]):
    """Endpoint principal de sincronização"""
    try:
        # Validar campos obrigatórios
        usuario = request.get("usuario")
        client_uuid = request.get("client_uuid")
        dados = request.get("dados", {})
        
        if not usuario:
            raise HTTPException(status_code=400, detail="Campo 'usuario' é obrigatório")
        
        if not client_uuid:
            raise HTTPException(status_code=400, detail="Campo 'client_uuid' é obrigatório")
        
        if not dados:
            raise HTTPException(status_code=400, detail="Campo 'dados' não pode estar vazio")
        
        print(f"🔄 Iniciando sincronização para usuário: {usuario}")
        
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
            novos = 0
            duplicados = 0
            
            for policial_data in dados["policiais"]:
                uuid_local = policial_data.get("uuid_local")
                if not uuid_local:
                    resultado["erros"].append("Policial sem UUID local")
                    continue
                
                if db.is_synced(usuario, "policial", uuid_local):
                    duplicados += 1
                    continue
                
                try:
                    policial_id = db.insert_or_get_policial(policial_data)
                    db.mark_synced(usuario, "policial", uuid_local, policial_id, calculate_hash(policial_data))
                    novos += 1
                    resultado["detalhes"].append(f"Policial {policial_data['matricula']} sincronizado")
                except Exception as e:
                    resultado["erros"].append(f"Erro ao sincronizar policial: {str(e)}")
            
            resultado["resumo"]["policiais"] = {"novos": novos, "duplicados": duplicados}
            total_novos += novos
            total_duplicados += duplicados
        
        # Processar proprietários
        if "proprietarios" in dados:
            novos = 0
            duplicados = 0
            
            for prop_data in dados["proprietarios"]:
                uuid_local = prop_data.get("uuid_local")
                if not uuid_local:
                    resultado["erros"].append("Proprietário sem UUID local")
                    continue
                
                if db.is_synced(usuario, "proprietario", uuid_local):
                    duplicados += 1
                    continue
                
                try:
                    prop_id = db.insert_or_get_proprietario(prop_data)
                    db.mark_synced(usuario, "proprietario", uuid_local, prop_id, calculate_hash(prop_data))
                    novos += 1
                    resultado["detalhes"].append(f"Proprietário {prop_data['documento']} sincronizado")
                except Exception as e:
                    resultado["erros"].append(f"Erro ao sincronizar proprietário: {str(e)}")
            
            resultado["resumo"]["proprietarios"] = {"novos": novos, "duplicados": duplicados}
            total_novos += novos
            total_duplicados += duplicados
        
        # Processar ocorrências
        if "ocorrencias" in dados:
            novos = 0
            duplicados = 0
            
            for ocor_data in dados["ocorrencias"]:
                uuid_local = ocor_data.get("uuid_local")
                if not uuid_local:
                    resultado["erros"].append("Ocorrência sem UUID local")
                    continue
                
                if db.is_synced(usuario, "ocorrencia", uuid_local):
                    duplicados += 1
                    continue
                
                try:
                    # Processar policial condutor
                    policial_data = ocor_data.get("policial_condutor", {})
                    policial_id = db.insert_or_get_policial(policial_data)
                    
                    # Inserir ocorrência
                    ocorrencia_id = db.insert_ocorrencia(ocor_data, policial_id)
                    
                    # Processar itens apreendidos
                    for item_data in ocor_data.get("itens_apreendidos", []):
                        prop_data = item_data.get("proprietario", {})
                        prop_id = db.insert_or_get_proprietario(prop_data)
                        db.insert_item_apreendido(item_data, ocorrencia_id, prop_id, policial_id)
                    
                    db.mark_synced(usuario, "ocorrencia", uuid_local, ocorrencia_id, calculate_hash(ocor_data))
                    novos += 1
                    resultado["detalhes"].append(f"Ocorrência {ocor_data['numero_genesis']} sincronizada")
                    
                except Exception as e:
                    resultado["erros"].append(f"Erro ao sincronizar ocorrência: {str(e)}")
            
            resultado["resumo"]["ocorrencias"] = {"novos": novos, "duplicados": duplicados}
            total_novos += novos
            total_duplicados += duplicados
        
        # Registrar log
        status = "sucesso" if not resultado["erros"] else "parcial"
        sync_id = db.log_sync(usuario, client_uuid, total_novos + total_duplicados, total_novos, total_duplicados, status, json.dumps(resultado["resumo"]))
        resultado["sync_id"] = sync_id
        
        print(f"✅ Sincronização concluída: {total_novos} novos, {total_duplicados} duplicados")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro durante sincronização: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/sincronizar/status/{usuario}")
async def get_sync_status(usuario: str):
    """Obtém status de sincronização de um usuário"""
    try:
        # Última sincronização
        last_sync = db.execute_query(
            "SELECT * FROM sync_log WHERE usuario = ? ORDER BY timestamp DESC LIMIT 1",
            (usuario,)
        )
        
        # Total de sincronizações
        total_syncs = db.execute_query(
            "SELECT COUNT(*) as count FROM sync_log WHERE usuario = ?",
            (usuario,)
        )[0]["count"]
        
        # Total de registros sincronizados
        total_records = db.execute_query(
            "SELECT COUNT(*) as count FROM registro_sincronizado WHERE usuario = ?",
            (usuario,)
        )[0]["count"]
        
        return {
            "usuario": usuario,
            "ultima_sincronizacao": last_sync[0]["timestamp"] if last_sync else None,
            "total_sincronizacoes": total_syncs,
            "total_registros_sincronizados": total_records,
            "status_ultima_sync": last_sync[0]["status"] if last_sync else "nunca_sincronizado"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@app.get("/sincronizar/historico/{usuario}")
async def get_sync_history(usuario: str, limit: int = 10):
    """Obtém histórico de sincronizações"""
    try:
        historico = db.execute_query(
            "SELECT * FROM sync_log WHERE usuario = ? ORDER BY timestamp DESC LIMIT ?",
            (usuario, limit)
        )
        
        return historico
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico: {str(e)}")

@app.get("/sincronizar/usuarios")
async def list_synced_users():
    """Lista usuários que já sincronizaram"""
    try:
        usuarios = db.execute_query("SELECT DISTINCT usuario FROM sync_log")
        return {"usuarios": [u["usuario"] for u in usuarios]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")

@app.get("/estatisticas")
async def get_statistics():
    """Obtém estatísticas gerais"""
    try:
        stats = {}
        
        # Contar registros por tabela
        for table in ["policial", "proprietario", "ocorrencia", "item_apreendido"]:
            count = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")[0]["count"]
            stats[f"total_{table}s"] = count
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando SECRIMPO Sync API...")
    print(f"📊 Banco de dados: {DATABASE_PATH}")
    print(f"🌐 Servidor: http://{API_HOST}:{API_PORT}")
    print("📋 Endpoints disponíveis:")
    print("   POST /sincronizar - Sincronizar dados")
    print("   POST /sincronizar/teste - Testar conectividade")
    print("   GET /sincronizar/status/{usuario} - Status do usuário")
    print("   GET /sincronizar/historico/{usuario} - Histórico do usuário")
    print("   GET /sincronizar/usuarios - Listar usuários")
    print("   GET /estatisticas - Estatísticas gerais")
    print()
    
    try:
        uvicorn.run(app, host=API_HOST, port=API_PORT, reload=False)
    except KeyboardInterrupt:
        print("\n⏹️ Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
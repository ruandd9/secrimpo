#!/usr/bin/env python3
"""
SECRIMPO - Sistema de Armazenamento Compartilhado
Configuração para pasta compartilhada em rede local
"""
import os
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
import json

class SharedStorageManager:
    """Gerenciador de armazenamento compartilhado"""
    
    def __init__(self, shared_path=None):
        # Configurações padrão
        if shared_path:
            self.shared_path = Path(shared_path)
        else:
            self.shared_path = self._detect_shared_path()
        self.local_backup_path = Path("backup")
        self.config_file = "shared_config.json"
        
        # Criar diretórios necessários
        self._setup_directories()
    
    def _detect_shared_path(self):
        """Detecta automaticamente pasta compartilhada"""
        possible_paths = [
            r"\\servidor\SecrimpoData",  # Windows SMB
            r"Z:\SecrimpoData",          # Unidade mapeada
            "/mnt/secrimpo",             # Linux mount
            "/media/secrimpo",           # Linux media
            "C:\\SecrimpoShared",        # Local compartilhado
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"[CHECK] Pasta compartilhada encontrada: {path}")
                return Path(path)
        
        # Se não encontrar, usar pasta local
        local_shared = Path("shared_data")
        local_shared.mkdir(exist_ok=True)
        print(f"[INFO] Usando pasta local: {local_shared}")
        return local_shared
    
    def _setup_directories(self):
        """Cria estrutura de diretórios necessária"""
        try:
            # Pasta principal compartilhada
            self.shared_path.mkdir(exist_ok=True)
            
            # Subpastas
            (self.shared_path / "database").mkdir(exist_ok=True)
            (self.shared_path / "exports").mkdir(exist_ok=True)
            (self.shared_path / "backups").mkdir(exist_ok=True)
            (self.shared_path / "logs").mkdir(exist_ok=True)
            
            # Pasta de backup local
            self.local_backup_path.mkdir(exist_ok=True)
            
            print(f"[CHECK] Estrutura de diretórios criada em: {self.shared_path}")
            
        except Exception as e:
            print(f"[ERROR] Erro ao criar diretórios: {e}")
            raise
    
    def get_database_path(self):
        """Retorna caminho do banco compartilhado"""
        return self.shared_path / "database" / "secrimpo.db"
    
    def get_exports_path(self):
        """Retorna caminho da pasta de exportações"""
        return self.shared_path / "exports"
    
    def setup_shared_database(self):
        """Configura banco de dados compartilhado"""
        shared_db = self.get_database_path()
        local_db = Path("secrimpo.db")
        
        try:
            # Se banco local existe e compartilhado não, migrar
            if local_db.exists() and not shared_db.exists():
                print("[INFO] Migrando banco local para compartilhado...")
                shutil.copy2(local_db, shared_db)
                print(f"[CHECK] Banco migrado para: {shared_db}")
            
            # Se banco compartilhado não existe, criar novo
            elif not shared_db.exists():
                print("[INFO] Criando novo banco compartilhado...")
                self._create_empty_database(shared_db)
            
            # Configurar WAL mode para melhor concorrência
            self._setup_wal_mode(shared_db)
            
            # Criar backup do banco local
            if local_db.exists():
                backup_name = f"secrimpo_local_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                shutil.copy2(local_db, self.local_backup_path / backup_name)
                print(f"[CHECK] Backup local criado: {backup_name}")
            
            return str(shared_db)
            
        except Exception as e:
            print(f"[ERROR] Erro ao configurar banco compartilhado: {e}")
            raise
    
    def _create_empty_database(self, db_path):
        """Cria banco de dados vazio com estrutura"""
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Criar tabelas (estrutura do SECRIMPO)
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS policial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                matricula TEXT UNIQUE NOT NULL,
                graduacao TEXT NOT NULL,
                unidade TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS proprietario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT UNIQUE NOT NULL,
                tipo_documento TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ocorrencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_genesis TEXT UNIQUE NOT NULL,
                unidade_fato TEXT NOT NULL,
                data_apreensao DATE NOT NULL,
                lei_infringida TEXT NOT NULL,
                artigo TEXT NOT NULL,
                policial_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (policial_id) REFERENCES policial (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS item_apreendido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                especie TEXT NOT NULL,
                item TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                descricao TEXT,
                ocorrencia_id INTEGER,
                proprietario_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ocorrencia_id) REFERENCES ocorrencia (id),
                FOREIGN KEY (proprietario_id) REFERENCES proprietario (id)
            )
            """
        ]
        
        for sql in tables_sql:
            cursor.execute(sql)
        
        conn.commit()
        conn.close()
        print(f"[CHECK] Banco de dados criado: {db_path}")
    
    def _setup_wal_mode(self, db_path):
        """Configura SQLite em modo WAL para melhor concorrência"""
        try:
            conn = sqlite3.connect(str(db_path))
            
            # Habilitar WAL mode
            conn.execute("PRAGMA journal_mode=WAL;")
            
            # Configurações de performance para rede
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA cache_size=10000;")
            conn.execute("PRAGMA temp_store=MEMORY;")
            conn.execute("PRAGMA mmap_size=268435456;")  # 256MB
            conn.execute("PRAGMA wal_autocheckpoint=1000;")
            
            conn.commit()
            conn.close()
            
            print("[CHECK] WAL mode configurado para concorrência")
            
        except Exception as e:
            print(f"[WARNING] Erro ao configurar WAL: {e}")
    
    def create_backup(self):
        """Cria backup do banco compartilhado"""
        try:
            shared_db = self.get_database_path()
            if not shared_db.exists():
                print("[WARNING] Banco compartilhado não existe")
                return None
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"secrimpo_backup_{timestamp}.db"
            backup_path = self.shared_path / "backups" / backup_name
            
            shutil.copy2(shared_db, backup_path)
            
            print(f"[CHECK] Backup criado: {backup_name}")
            return str(backup_path)
            
        except Exception as e:
            print(f"[ERROR] Erro ao criar backup: {e}")
            return None
    
    def test_connectivity(self):
        """Testa conectividade com pasta compartilhada"""
        try:
            # Teste 1: Verificar se pasta existe
            if not self.shared_path.exists():
                return False, "Pasta compartilhada não acessível"
            
            # Teste 2: Verificar permissões de escrita
            test_file = self.shared_path / "test_write.tmp"
            with open(test_file, "w") as f:
                f.write("teste")
            test_file.unlink()
            
            # Teste 3: Verificar banco de dados
            shared_db = self.get_database_path()
            if shared_db.exists():
                conn = sqlite3.connect(str(shared_db), timeout=10)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master")
                conn.close()
            
            return True, "Conectividade OK"
            
        except Exception as e:
            return False, f"Erro de conectividade: {e}"
    
    def save_config(self, config_data):
        """Salva configuração do armazenamento compartilhado"""
        config = {
            "shared_path": str(self.shared_path),
            "setup_date": datetime.now().isoformat(),
            "version": "1.0.0",
            **config_data
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"[CHECK] Configuração salva: {self.config_file}")
    
    def load_config(self):
        """Carrega configuração salva"""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_status(self):
        """Retorna status do armazenamento compartilhado"""
        status = {
            "shared_path": str(self.shared_path),
            "shared_path_exists": self.shared_path.exists(),
            "database_path": str(self.get_database_path()),
            "database_exists": self.get_database_path().exists(),
            "exports_path": str(self.get_exports_path()),
            "connectivity": self.test_connectivity(),
            "timestamp": datetime.now().isoformat()
        }
        
        return status


def main():
    """Função principal para configurar armazenamento compartilhado"""
    print("=" * 60)
    print("🗂️  SECRIMPO - Configuração de Armazenamento Compartilhado")
    print("=" * 60)
    
    # Solicitar caminho da pasta compartilhada
    print("\n📁 Configuração da Pasta Compartilhada:")
    print("1. Pasta de rede (ex: \\\\servidor\\SecrimpoData)")
    print("2. Unidade mapeada (ex: Z:\\SecrimpoData)")
    print("3. Pasta local compartilhada (ex: C:\\SecrimpoShared)")
    print("4. Detectar automaticamente")
    
    choice = input("\nEscolha uma opção (1-4): ").strip()
    
    shared_path = None
    if choice == "1":
        shared_path = input("Digite o caminho da rede (ex: \\\\servidor\\SecrimpoData): ").strip()
    elif choice == "2":
        shared_path = input("Digite a unidade mapeada (ex: Z:\\SecrimpoData): ").strip()
    elif choice == "3":
        shared_path = input("Digite o caminho local (ex: C:\\SecrimpoShared): ").strip()
    # choice == "4" ou qualquer outra: detectar automaticamente
    
    try:
        # Inicializar gerenciador
        storage = SharedStorageManager(shared_path)
        
        # Testar conectividade
        print(f"\n🔍 Testando conectividade com: {storage.shared_path}")
        is_connected, message = storage.test_connectivity()
        
        if not is_connected:
            print(f"❌ {message}")
            print("\n💡 Dicas para resolver:")
            print("- Verifique se a pasta existe e está acessível")
            print("- Confirme permissões de leitura/escrita")
            print("- Teste conectividade de rede")
            return False
        
        print(f"✅ {message}")
        
        # Configurar banco compartilhado
        print(f"\n📊 Configurando banco de dados compartilhado...")
        db_path = storage.setup_shared_database()
        print(f"✅ Banco configurado: {db_path}")
        
        # Criar backup inicial
        print(f"\n💾 Criando backup inicial...")
        backup_path = storage.create_backup()
        if backup_path:
            print(f"✅ Backup criado: {backup_path}")
        
        # Salvar configuração
        config_data = {
            "user_choice": choice,
            "manual_path": shared_path if choice in ["1", "2", "3"] else None
        }
        storage.save_config(config_data)
        
        # Mostrar status final
        print(f"\n📋 Status Final:")
        status = storage.get_status()
        for key, value in status.items():
            if key != "timestamp":
                print(f"   {key}: {value}")
        
        print(f"\n🎉 Configuração concluída com sucesso!")
        print(f"\n📝 Próximos passos:")
        print(f"1. Compartilhe a pasta '{storage.shared_path}' com outros usuários")
        print(f"2. Execute este script em cada PC cliente")
        print(f"3. Inicie o SECRIMPO normalmente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante configuração: {e}")
        return False


if __name__ == "__main__":
    main()
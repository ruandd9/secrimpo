from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import date, datetime
import time
from jose import jwt
import os
from config import UNIDADES_DISPONIVEIS

# Import authentication
from auth.middleware import verify_license, require_permission, AuthContext, optional_verify_license
from auth.keyauth_config import auth_manager

# Configuração do banco de dados (usando config.py)
from config import DATABASE_URL

# Criar engine
engine = create_engine(DATABASE_URL, echo=True)
print(f"[INFO] Usando banco de dados: {DATABASE_URL}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# === MODELOS SQLALCHEMY ===
class Policial(Base):
    __tablename__ = 'policial'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=True, default=lambda: __import__('uuid').uuid4().hex)
    nome = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    graduacao = Column(String, nullable=False)
    unidade = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    ocorrencias_condutor = relationship('Ocorrencia', back_populates='policial_condutor')
    itens_apreendidos = relationship('ItemApreendido', back_populates='policial')

class Proprietario(Base):
    __tablename__ = 'proprietario'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=True, default=lambda: __import__('uuid').uuid4().hex)
    nome = Column(String, nullable=False)
    documento = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    itens_apreendidos = relationship('ItemApreendido', back_populates='proprietario')

class Ocorrencia(Base):
    __tablename__ = 'ocorrencia'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=True, default=lambda: __import__('uuid').uuid4().hex)
    numero_genesis = Column(String, nullable=False)
    unidade_fato = Column(String, nullable=False)
    data_apreensao = Column(Date, nullable=False)
    lei_infringida = Column(String, nullable=False)
    artigo = Column(String, nullable=False)
    policial_condutor_id = Column(Integer, ForeignKey('policial.id'), nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    policial_condutor = relationship('Policial', back_populates='ocorrencias_condutor')
    itens_apreendidos = relationship('ItemApreendido', back_populates='ocorrencia')

class ItemApreendido(Base):
    __tablename__ = 'item_apreendido'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=True, default=lambda: __import__('uuid').uuid4().hex)
    especie = Column(String, nullable=False)
    item = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)
    descricao_detalhada = Column(String, nullable=False)
    ocorrencia_id = Column(Integer, ForeignKey('ocorrencia.id'), nullable=False)
    proprietario_id = Column(Integer, ForeignKey('proprietario.id'), nullable=False)
    policial_id = Column(Integer, ForeignKey('policial.id'), nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    ocorrencia = relationship('Ocorrencia', back_populates='itens_apreendidos')
    proprietario = relationship('Proprietario', back_populates='itens_apreendidos')
    policial = relationship('Policial', back_populates='itens_apreendidos')

# Criar/atualizar tabelas (garantindo colunas novas no SQLite existente)
Base.metadata.create_all(bind=engine)

# Para bancos já existentes, garantir colunas novas via ALTER TABLE (somente SQLite)
def _ensure_sqlite_columns():
    try:
        if not str(engine.url).startswith("sqlite"):  # apenas para sqlite
            return
        with engine.connect() as conn:
            # Helper para checar se coluna existe
            def has_column(table: str, column: str) -> bool:
                res = conn.execute(text(f"PRAGMA table_info({table});"))
                return any(row[1] == column for row in res.fetchall())

            # Tabela policial
            if not has_column('policial', 'uuid'):
                conn.execute(text("ALTER TABLE policial ADD COLUMN uuid TEXT UNIQUE"))
            if not has_column('policial', 'created_at'):
                conn.execute(text("ALTER TABLE policial ADD COLUMN created_at DATETIME"))
            if not has_column('policial', 'updated_at'):
                conn.execute(text("ALTER TABLE policial ADD COLUMN updated_at DATETIME"))

            # Tabela proprietario
            if not has_column('proprietario', 'uuid'):
                conn.execute(text("ALTER TABLE proprietario ADD COLUMN uuid TEXT UNIQUE"))
            if not has_column('proprietario', 'created_at'):
                conn.execute(text("ALTER TABLE proprietario ADD COLUMN created_at DATETIME"))
            if not has_column('proprietario', 'updated_at'):
                conn.execute(text("ALTER TABLE proprietario ADD COLUMN updated_at DATETIME"))

            # Tabela ocorrencia
            if not has_column('ocorrencia', 'uuid'):
                conn.execute(text("ALTER TABLE ocorrencia ADD COLUMN uuid TEXT UNIQUE"))
            if not has_column('ocorrencia', 'created_at'):
                conn.execute(text("ALTER TABLE ocorrencia ADD COLUMN created_at DATETIME"))
            if not has_column('ocorrencia', 'updated_at'):
                conn.execute(text("ALTER TABLE ocorrencia ADD COLUMN updated_at DATETIME"))

            # Tabela item_apreendido
            if not has_column('item_apreendido', 'uuid'):
                conn.execute(text("ALTER TABLE item_apreendido ADD COLUMN uuid TEXT UNIQUE"))
            if not has_column('item_apreendido', 'created_at'):
                conn.execute(text("ALTER TABLE item_apreendido ADD COLUMN created_at DATETIME"))
            if not has_column('item_apreendido', 'updated_at'):
                conn.execute(text("ALTER TABLE item_apreendido ADD COLUMN updated_at DATETIME"))
    except Exception as _e:
        # Evita quebrar inicialização; logs podem ser adicionados futuramente
        pass

_ensure_sqlite_columns()

# === SCHEMAS PYDANTIC ===
class PolicialBase(BaseModel):
    nome: str
    matricula: str
    graduacao: str
    unidade: str

class PolicialCreate(PolicialBase):
    pass

class PolicialResponse(PolicialBase):
    id: int
    uuid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ProprietarioBase(BaseModel):
    nome: str
    documento: str

class ProprietarioCreate(ProprietarioBase):
    pass

class ProprietarioResponse(ProprietarioBase):
    id: int
    uuid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class OcorrenciaBase(BaseModel):
    numero_genesis: str
    unidade_fato: str
    data_apreensao: date
    lei_infringida: str
    artigo: str
    policial_condutor_id: int

class OcorrenciaCreate(OcorrenciaBase):
    pass

class OcorrenciaResponse(OcorrenciaBase):
    id: int
    uuid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ItemApreendidoBase(BaseModel):
    especie: str
    item: str
    quantidade: int
    descricao_detalhada: str
    ocorrencia_id: int
    proprietario_id: int
    policial_id: int

class ItemApreendidoCreate(ItemApreendidoBase):
    pass

class ItemApreendidoResponse(ItemApreendidoBase):
    id: int
    uuid: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# === APLICAÇÃO FASTAPI ===
app = FastAPI(
    title="SECRIMPO API",
    description="API para sistema de registro de ocorrências policiais",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === ENDPOINTS ===
@app.get("/")
async def root():
    return {"message": "SECRIMPO API está funcionando!", "version": "1.0.0"}

# === AUTHENTICATION ENDPOINTS ===
@app.post("/auth/validate")
async def validate_auth(auth: AuthContext = Depends(verify_license)):
    """Validate JWT token and return user permissions"""
    return {
        "valid": True,
        "user": {
            "username": auth.username,
            "subscription": auth.subscription,
            "expires": auth.expires,
            "created_at": auth.created_at,
            "last_login": auth.last_login
        },
        "permissions": auth.permissions
    }

# JWT settings for username/password login
JWT_SECRET = os.getenv("APP_JWT_SECRET", "dev-secret-please-change")
JWT_ALG = "HS256"
JWT_EXP_SECONDS = 60 * 60 * 8

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/login")
async def login_user(payload: LoginRequest):
    """Login com usuário/senha via KeyAuth; retorna JWT para o frontend."""
    result = auth_manager.login_user(payload.username, payload.password)
    if not result.get("valid"):
        raise HTTPException(status_code=401, detail=result.get("error", "Invalid credentials"))

    user = result["user_data"]
    permissions = auth_manager.get_user_permissions(user["subscription"])  # mapear permissões

    now = int(time.time())
    claims = {
        "sub": user["username"],
        "subscription": user["subscription"],
        "permissions": permissions,
        "iat": now,
        "exp": now + JWT_EXP_SECONDS,
    }
    token = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALG)
    return {"access_token": token, "token_type": "bearer", "user": user, "permissions": permissions}

@app.get("/auth/user-info")
async def get_user_info(auth: AuthContext = Depends(verify_license)):
    """Get current user information"""
    return {
        "username": auth.username,
        "subscription": auth.subscription,
        "permissions": auth.permissions,
        "expires": auth.expires
    }

# POLICIAIS
@app.post("/policiais/", response_model=PolicialResponse)
@require_permission("create_occurrence")
async def criar_policial(policial: PolicialCreate, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    # Verifica se matrícula já existe
    existing = db.query(Policial).filter(Policial.matricula == policial.matricula).first()
    if existing:
        raise HTTPException(status_code=400, detail="Matrícula já existe")
    
    db_policial = Policial(**policial.dict())
    db.add(db_policial)
    db.commit()
    db.refresh(db_policial)
    
    # Log action
    auth_manager.log_user_action(auth.username, "CREATE_POLICIAL", f"Matricula: {policial.matricula}")
    
    return db_policial

@app.get("/policiais/", response_model=List[PolicialResponse])
@require_permission("view_all_occurrences")
async def listar_policiais(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    return db.query(Policial).offset(skip).limit(limit).all()

@app.get("/policiais/{policial_id}", response_model=PolicialResponse)
@require_permission("view_all_occurrences")
async def obter_policial(policial_id: int, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    policial = db.query(Policial).filter(Policial.id == policial_id).first()
    if not policial:
        raise HTTPException(status_code=404, detail="Policial não encontrado")
    return policial

# PROPRIETÁRIOS
@app.post("/proprietarios/", response_model=ProprietarioResponse)
@require_permission("create_occurrence")
async def criar_proprietario(proprietario: ProprietarioCreate, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    db_proprietario = Proprietario(**proprietario.dict())
    db.add(db_proprietario)
    db.commit()
    db.refresh(db_proprietario)
    
    # Log action
    auth_manager.log_user_action(auth.username, "CREATE_PROPRIETARIO", f"Documento: {proprietario.documento}")
    
    return db_proprietario

@app.get("/proprietarios/", response_model=List[ProprietarioResponse])
@require_permission("view_all_occurrences")
async def listar_proprietarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    return db.query(Proprietario).offset(skip).limit(limit).all()

# OCORRÊNCIAS
@app.post("/ocorrencias/", response_model=OcorrenciaResponse)
@require_permission("create_occurrence")
async def criar_ocorrencia(ocorrencia: OcorrenciaCreate, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    # Verifica se policial existe
    policial = db.query(Policial).filter(Policial.id == ocorrencia.policial_condutor_id).first()
    if not policial:
        raise HTTPException(status_code=400, detail="Policial condutor não encontrado")
    
    db_ocorrencia = Ocorrencia(**ocorrencia.dict())
    db.add(db_ocorrencia)
    db.commit()
    db.refresh(db_ocorrencia)
    
    # Log action
    auth_manager.log_user_action(auth.username, "CREATE_OCORRENCIA", f"Genesis: {ocorrencia.numero_genesis}")
    
    return db_ocorrencia

@app.get("/ocorrencias/", response_model=List[OcorrenciaResponse])
@require_permission("view_all_occurrences")
async def listar_ocorrencias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    return db.query(Ocorrencia).offset(skip).limit(limit).all()

# ITENS APREENDIDOS
@app.post("/itens/", response_model=ItemApreendidoResponse)
@require_permission("create_occurrence")
async def criar_item(item: ItemApreendidoCreate, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    # Verifica se todas as referências existem
    ocorrencia = db.query(Ocorrencia).filter(Ocorrencia.id == item.ocorrencia_id).first()
    if not ocorrencia:
        raise HTTPException(status_code=400, detail="Ocorrência não encontrada")
    
    proprietario = db.query(Proprietario).filter(Proprietario.id == item.proprietario_id).first()
    if not proprietario:
        raise HTTPException(status_code=400, detail="Proprietário não encontrado")
    
    policial = db.query(Policial).filter(Policial.id == item.policial_id).first()
    if not policial:
        raise HTTPException(status_code=400, detail="Policial não encontrado")
    
    db_item = ItemApreendido(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Log action
    auth_manager.log_user_action(auth.username, "CREATE_ITEM", f"Item: {item.item}, Qtd: {item.quantidade}")
    
    return db_item

@app.get("/itens/", response_model=List[ItemApreendidoResponse])
@require_permission("view_all_occurrences")
async def listar_itens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    return db.query(ItemApreendido).offset(skip).limit(limit).all()

@app.get("/itens/ocorrencia/{ocorrencia_id}", response_model=List[ItemApreendidoResponse])
@require_permission("view_all_occurrences")
async def listar_itens_por_ocorrencia(ocorrencia_id: int, db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    return db.query(ItemApreendido).filter(ItemApreendido.ocorrencia_id == ocorrencia_id).all()

# UNIDADES DISPONÍVEIS
@app.get("/unidades/")
async def obter_unidades():
    return {"unidades": UNIDADES_DISPONIVEIS}

# === SYNC ENDPOINTS (mínimo viável) ===
class SyncChangesRequest(BaseModel):
    updated_since: Optional[datetime] = None
    limit: int = 500

class SyncBatchRequest(BaseModel):
    policiais: Optional[List[dict]] = None
    proprietarios: Optional[List[dict]] = None
    ocorrencias: Optional[List[dict]] = None
    itens: Optional[List[dict]] = None

@app.get("/sync/ping")
async def sync_ping():
    return {"status": "ok", "time": int(time.time())}

@app.post("/sync/changes")
async def sync_changes(payload: SyncChangesRequest, db: Session = Depends(get_db)):
    since = payload.updated_since or datetime.fromtimestamp(0)
    lim = max(1, min(payload.limit, 2000))

    def serialize_policial(p: Policial):
        return {
            "id": p.id,
            "uuid": p.uuid,
            "nome": p.nome,
            "matricula": p.matricula,
            "graduacao": p.graduacao,
            "unidade": p.unidade,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }

    def serialize_proprietario(p: Proprietario):
        return {
            "id": p.id,
            "uuid": p.uuid,
            "nome": p.nome,
            "documento": p.documento,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }

    def serialize_ocorrencia(o: Ocorrencia):
        return {
            "id": o.id,
            "uuid": o.uuid,
            "numero_genesis": o.numero_genesis,
            "unidade_fato": o.unidade_fato,
            "data_apreensao": o.data_apreensao.isoformat() if o.data_apreensao else None,
            "lei_infringida": o.lei_infringida,
            "artigo": o.artigo,
            "policial_condutor_id": o.policial_condutor_id,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "updated_at": o.updated_at.isoformat() if o.updated_at else None,
        }

    def serialize_item(i: ItemApreendido):
        return {
            "id": i.id,
            "uuid": i.uuid,
            "especie": i.especie,
            "item": i.item,
            "quantidade": i.quantidade,
            "descricao_detalhada": i.descricao_detalhada,
            "ocorrencia_id": i.ocorrencia_id,
            "proprietario_id": i.proprietario_id,
            "policial_id": i.policial_id,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        }

    policiais = db.query(Policial).filter((Policial.updated_at != None) & (Policial.updated_at > since)).limit(lim).all()
    proprietarios = db.query(Proprietario).filter((Proprietario.updated_at != None) & (Proprietario.updated_at > since)).limit(lim).all()
    ocorrencias = db.query(Ocorrencia).filter((Ocorrencia.updated_at != None) & (Ocorrencia.updated_at > since)).limit(lim).all()
    itens = db.query(ItemApreendido).filter((ItemApreendido.updated_at != None) & (ItemApreendido.updated_at > since)).limit(lim).all()

    return {
        "policiais": [serialize_policial(p) for p in policiais],
        "proprietarios": [serialize_proprietario(p) for p in proprietarios],
        "ocorrencias": [serialize_ocorrencia(o) for o in ocorrencias],
        "itens": [serialize_item(i) for i in itens],
    }

@app.post("/sync/batch")
async def sync_batch(payload: SyncBatchRequest, db: Session = Depends(get_db)):
    # Upsert simplificado por uuid; se faltar uuid, tenta chave natural
    now = datetime.utcnow()

    def upsert_policial(d: dict):
        uuid_val = d.get("uuid")
        q = db.query(Policial)
        if uuid_val:
            existing = q.filter(Policial.uuid == uuid_val).first()
        else:
            existing = q.filter(Policial.matricula == d.get("matricula")).first()
        if existing:
            # last-write-wins por updated_at
            incoming_updated = d.get("updated_at")
            if incoming_updated:
                try:
                    inc_dt = datetime.fromisoformat(incoming_updated)
                    if not existing.updated_at or inc_dt >= existing.updated_at:
                        for k in ["nome","matricula","graduacao","unidade"]:
                            if k in d: setattr(existing, k, d[k])
                        existing.updated_at = inc_dt
            
                except Exception:
                    pass
            return existing
        obj = Policial(
            uuid=uuid_val or __import__('uuid').uuid4().hex,
            nome=d.get("nome"),
            matricula=d.get("matricula"),
            graduacao=d.get("graduacao"),
            unidade=d.get("unidade"),
            created_at=now,
            updated_at=now,
        )
        db.add(obj)
        return obj

    def upsert_proprietario(d: dict):
        uuid_val = d.get("uuid")
        q = db.query(Proprietario)
        if uuid_val:
            existing = q.filter(Proprietario.uuid == uuid_val).first()
        else:
            existing = q.filter(Proprietario.documento == d.get("documento")).first()
        if existing:
            incoming_updated = d.get("updated_at")
            if incoming_updated:
                try:
                    inc_dt = datetime.fromisoformat(incoming_updated)
                    if not existing.updated_at or inc_dt >= existing.updated_at:
                        for k in ["nome","documento"]:
                            if k in d: setattr(existing, k, d[k])
                        existing.updated_at = inc_dt
                except Exception:
                    pass
            return existing
        obj = Proprietario(
            uuid=uuid_val or __import__('uuid').uuid4().hex,
            nome=d.get("nome"),
            documento=d.get("documento"),
            created_at=now,
            updated_at=now,
        )
        db.add(obj)
        return obj

    def upsert_ocorrencia(d: dict):
        uuid_val = d.get("uuid")
        q = db.query(Ocorrencia)
        if uuid_val:
            existing = q.filter(Ocorrencia.uuid == uuid_val).first()
        else:
            existing = q.filter(Ocorrencia.numero_genesis == d.get("numero_genesis")).first()
        if existing:
            incoming_updated = d.get("updated_at")
            if incoming_updated:
                try:
                    inc_dt = datetime.fromisoformat(incoming_updated)
                    if not existing.updated_at or inc_dt >= existing.updated_at:
                        for k in ["numero_genesis","unidade_fato","lei_infringida","artigo"]:
                            if k in d: setattr(existing, k, d[k])
                        if d.get("data_apreensao"):
                            existing.data_apreensao = date.fromisoformat(d["data_apreensao"])
                        if d.get("policial_condutor_id"):
                            existing.policial_condutor_id = d["policial_condutor_id"]
                        existing.updated_at = inc_dt
                except Exception:
                    pass
            return existing
        obj = Ocorrencia(
            uuid=uuid_val or __import__('uuid').uuid4().hex,
            numero_genesis=d.get("numero_genesis"),
            unidade_fato=d.get("unidade_fato"),
            data_apreensao=date.fromisoformat(d.get("data_apreensao")) if d.get("data_apreensao") else None,
            lei_infringida=d.get("lei_infringida"),
            artigo=d.get("artigo"),
            policial_condutor_id=d.get("policial_condutor_id"),
            created_at=now,
            updated_at=now,
        )
        db.add(obj)
        return obj

    def upsert_item(d: dict):
        uuid_val = d.get("uuid")
        q = db.query(ItemApreendido)
        if uuid_val:
            existing = q.filter(ItemApreendido.uuid == uuid_val).first()
        else:
            # Sem chave natural global, cria novo
            existing = None
        if existing:
            incoming_updated = d.get("updated_at")
            if incoming_updated:
                try:
                    inc_dt = datetime.fromisoformat(incoming_updated)
                    if not existing.updated_at or inc_dt >= existing.updated_at:
                        for k in ["especie","item","quantidade","descricao_detalhada","ocorrencia_id","proprietario_id","policial_id"]:
                            if k in d: setattr(existing, k, d[k])
                        existing.updated_at = inc_dt
                except Exception:
                    pass
            return existing
        obj = ItemApreendido(
            uuid=uuid_val or __import__('uuid').uuid4().hex,
            especie=d.get("especie"),
            item=d.get("item"),
            quantidade=d.get("quantidade"),
            descricao_detalhada=d.get("descricao_detalhada"),
            ocorrencia_id=d.get("ocorrencia_id"),
            proprietario_id=d.get("proprietario_id"),
            policial_id=d.get("policial_id"),
            created_at=now,
            updated_at=now,
        )
        db.add(obj)
        return obj

    counts = {"policiais":0, "proprietarios":0, "ocorrencias":0, "itens":0}
    try:
        for d in (payload.policiais or []):
            upsert_policial(d); counts["policiais"] += 1
        for d in (payload.proprietarios or []):
            upsert_proprietario(d); counts["proprietarios"] += 1
        for d in (payload.ocorrencias or []):
            upsert_ocorrencia(d); counts["ocorrencias"] += 1
        for d in (payload.itens or []):
            upsert_item(d); counts["itens"] += 1
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no sync: {str(e)}")

    return {"status": "ok", "counts": counts}

# ESTATÍSTICAS
@app.get("/estatisticas/")
@require_permission("view_statistics")
async def obter_estatisticas(db: Session = Depends(get_db), auth: AuthContext = Depends(verify_license)):
    total_ocorrencias = db.query(Ocorrencia).count()
    total_policiais = db.query(Policial).count()
    total_proprietarios = db.query(Proprietario).count()
    total_itens = db.query(ItemApreendido).count()
    
    # Log access
    auth_manager.log_user_action(auth.username, "VIEW_STATISTICS", "Accessed system statistics")
    
    return {
        "total_ocorrencias": total_ocorrencias,
        "total_policiais": total_policiais,
        "total_proprietarios": total_proprietarios,
        "total_itens": total_itens
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# === ENDPOINTS DE EXPORTAÇÃO DE PLANILHAS ===
from services.excel_export import ExcelExportService

@app.get("/export/relatorio_completo")
@require_permission("export_reports")
async def export_relatorio_completo(
    data_inicio: date = Query(..., description="Data inicial no formato YYYY-MM-DD"),
    data_fim: date = Query(..., description="Data final no formato YYYY-MM-DD"),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(verify_license)
):
    try:
        service = ExcelExportService(db)
        caminho = service.export_ocorrencias_completo(data_inicio, data_fim)
        nome = os.path.basename(caminho)
        
        # Log export action
        auth_manager.log_user_action(
            auth.username, 
            "EXPORT_COMPLETE_REPORT", 
            f"Period: {data_inicio} to {data_fim}"
        )
        
        return FileResponse(
            caminho,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=nome
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar exportação: {str(e)}")

@app.get("/export/resumo_mensal")
@require_permission("export_reports")
async def export_resumo_mensal(
    ano: int = Query(..., ge=2000, le=2100),
    mes: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(verify_license)
):
    try:
        service = ExcelExportService(db)
        caminho = service.export_resumo_mensal(ano, mes)
        nome = os.path.basename(caminho)
        return FileResponse(
            caminho,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=nome
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar exportação: {str(e)}")

@app.get("/export/por_policial/{policial_id}")
async def export_por_policial(
    policial_id: int,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):
    try:
        service = ExcelExportService(db)
        caminho = service.export_por_policial(policial_id, data_inicio, data_fim)
        nome = os.path.basename(caminho)
        return FileResponse(
            caminho,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=nome
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar exportação: {str(e)}")

@app.get("/export/estatisticas")
async def export_estatisticas(
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):
    try:
        service = ExcelExportService(db)
        caminho = service.export_estatisticas(data_inicio, data_fim)
        nome = os.path.basename(caminho)
        return FileResponse(
            caminho,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=nome
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar exportação: {str(e)}")
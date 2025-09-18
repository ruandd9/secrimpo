from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import date
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
    nome = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    graduacao = Column(String, nullable=False)
    unidade = Column(String, nullable=False)

    ocorrencias_condutor = relationship('Ocorrencia', back_populates='policial_condutor')
    itens_apreendidos = relationship('ItemApreendido', back_populates='policial')

class Proprietario(Base):
    __tablename__ = 'proprietario'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    documento = Column(String, nullable=False)

    itens_apreendidos = relationship('ItemApreendido', back_populates='proprietario')

class Ocorrencia(Base):
    __tablename__ = 'ocorrencia'
    id = Column(Integer, primary_key=True)
    numero_genesis = Column(String, nullable=False)
    unidade_fato = Column(String, nullable=False)
    data_apreensao = Column(Date, nullable=False)
    lei_infringida = Column(String, nullable=False)
    artigo = Column(String, nullable=False)
    policial_condutor_id = Column(Integer, ForeignKey('policial.id'), nullable=False)

    policial_condutor = relationship('Policial', back_populates='ocorrencias_condutor')
    itens_apreendidos = relationship('ItemApreendido', back_populates='ocorrencia')

class ItemApreendido(Base):
    __tablename__ = 'item_apreendido'
    id = Column(Integer, primary_key=True)
    especie = Column(String, nullable=False)
    item = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)
    descricao_detalhada = Column(String, nullable=False)
    ocorrencia_id = Column(Integer, ForeignKey('ocorrencia.id'), nullable=False)
    proprietario_id = Column(Integer, ForeignKey('proprietario.id'), nullable=False)
    policial_id = Column(Integer, ForeignKey('policial.id'), nullable=False)

    ocorrencia = relationship('Ocorrencia', back_populates='itens_apreendidos')
    proprietario = relationship('Proprietario', back_populates='itens_apreendidos')
    policial = relationship('Policial', back_populates='itens_apreendidos')

# Criar tabelas
Base.metadata.create_all(bind=engine)

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
    class Config:
        from_attributes = True

class ProprietarioBase(BaseModel):
    nome: str
    documento: str

class ProprietarioCreate(ProprietarioBase):
    pass

class ProprietarioResponse(ProprietarioBase):
    id: int
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
    """Validate authentication token and return user permissions"""
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
from fastapi import FastAPI, Depends, HTTPException
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

# Configuração do banco de dados
DATABASE_URL = "sqlite:///./secrimpo.db"
engine = create_engine(DATABASE_URL, echo=True)
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

# POLICIAIS
@app.post("/policiais/", response_model=PolicialResponse)
async def criar_policial(policial: PolicialCreate, db: Session = Depends(get_db)):
    # Verifica se matrícula já existe
    existing = db.query(Policial).filter(Policial.matricula == policial.matricula).first()
    if existing:
        raise HTTPException(status_code=400, detail="Matrícula já existe")
    
    db_policial = Policial(**policial.dict())
    db.add(db_policial)
    db.commit()
    db.refresh(db_policial)
    return db_policial

@app.get("/policiais/", response_model=List[PolicialResponse])
async def listar_policiais(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Policial).offset(skip).limit(limit).all()

@app.get("/policiais/{policial_id}", response_model=PolicialResponse)
async def obter_policial(policial_id: int, db: Session = Depends(get_db)):
    policial = db.query(Policial).filter(Policial.id == policial_id).first()
    if not policial:
        raise HTTPException(status_code=404, detail="Policial não encontrado")
    return policial

# PROPRIETÁRIOS
@app.post("/proprietarios/", response_model=ProprietarioResponse)
async def criar_proprietario(proprietario: ProprietarioCreate, db: Session = Depends(get_db)):
    db_proprietario = Proprietario(**proprietario.dict())
    db.add(db_proprietario)
    db.commit()
    db.refresh(db_proprietario)
    return db_proprietario

@app.get("/proprietarios/", response_model=List[ProprietarioResponse])
async def listar_proprietarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Proprietario).offset(skip).limit(limit).all()

# OCORRÊNCIAS
@app.post("/ocorrencias/", response_model=OcorrenciaResponse)
async def criar_ocorrencia(ocorrencia: OcorrenciaCreate, db: Session = Depends(get_db)):
    # Verifica se policial existe
    policial = db.query(Policial).filter(Policial.id == ocorrencia.policial_condutor_id).first()
    if not policial:
        raise HTTPException(status_code=400, detail="Policial condutor não encontrado")
    
    db_ocorrencia = Ocorrencia(**ocorrencia.dict())
    db.add(db_ocorrencia)
    db.commit()
    db.refresh(db_ocorrencia)
    return db_ocorrencia

@app.get("/ocorrencias/", response_model=List[OcorrenciaResponse])
async def listar_ocorrencias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Ocorrencia).offset(skip).limit(limit).all()

# ITENS APREENDIDOS
@app.post("/itens/", response_model=ItemApreendidoResponse)
async def criar_item(item: ItemApreendidoCreate, db: Session = Depends(get_db)):
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
    return db_item

@app.get("/itens/", response_model=List[ItemApreendidoResponse])
async def listar_itens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ItemApreendido).offset(skip).limit(limit).all()

@app.get("/itens/ocorrencia/{ocorrencia_id}", response_model=List[ItemApreendidoResponse])
async def listar_itens_por_ocorrencia(ocorrencia_id: int, db: Session = Depends(get_db)):
    return db.query(ItemApreendido).filter(ItemApreendido.ocorrencia_id == ocorrencia_id).all()

# UNIDADES DISPONÍVEIS
@app.get("/unidades/")
async def obter_unidades():
    return {"unidades": UNIDADES_DISPONIVEIS}

# ESTATÍSTICAS
@app.get("/estatisticas/")
async def obter_estatisticas(db: Session = Depends(get_db)):
    total_ocorrencias = db.query(Ocorrencia).count()
    total_policiais = db.query(Policial).count()
    total_proprietarios = db.query(Proprietario).count()
    total_itens = db.query(ItemApreendido).count()
    
    return {
        "total_ocorrencias": total_ocorrencias,
        "total_policiais": total_policiais,
        "total_proprietarios": total_proprietarios,
        "total_itens": total_itens
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
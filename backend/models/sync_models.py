"""
Modelos para sincronização de dados entre clientes locais e servidor central
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

Base = declarative_base()

class SyncLog(Base):
    """Log de sincronizações realizadas"""
    __tablename__ = 'sync_log'
    
    id = Column(Integer, primary_key=True)
    usuario = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_registros = Column(Integer, default=0)
    registros_novos = Column(Integer, default=0)
    registros_duplicados = Column(Integer, default=0)
    status = Column(String, default='sucesso')  # sucesso, erro, parcial
    detalhes = Column(Text)
    client_uuid = Column(String)  # UUID único do cliente

class RegistroSincronizado(Base):
    """Controle de registros já sincronizados para evitar duplicação"""
    __tablename__ = 'registro_sincronizado'
    
    id = Column(Integer, primary_key=True)
    usuario = Column(String, nullable=False)
    tipo_registro = Column(String, nullable=False)  # ocorrencia, policial, etc
    uuid_local = Column(String, nullable=False)  # UUID do registro no cliente
    id_central = Column(Integer, nullable=False)  # ID no banco central
    timestamp_sync = Column(DateTime, default=datetime.utcnow)
    hash_dados = Column(String)  # Hash dos dados para detectar mudanças

# === SCHEMAS PYDANTIC PARA SINCRONIZAÇÃO ===

class DadosOcorrencia(BaseModel):
    """Dados de uma ocorrência para sincronização"""
    uuid_local: str
    numero_genesis: str
    unidade_fato: str
    data_apreensao: str  # ISO format
    lei_infringida: str
    artigo: str
    policial_condutor: Dict[str, Any]  # Dados do policial
    itens_apreendidos: List[Dict[str, Any]]  # Lista de itens

class DadosPolicial(BaseModel):
    """Dados de um policial para sincronização"""
    uuid_local: str
    nome: str
    matricula: str
    graduacao: str
    unidade: str

class DadosProprietario(BaseModel):
    """Dados de um proprietário para sincronização"""
    uuid_local: str
    nome: str
    documento: str

class SincronizacaoRequest(BaseModel):
    """Request de sincronização completa"""
    usuario: str
    client_uuid: str
    timestamp_cliente: datetime
    dados: Dict[str, List[Dict[str, Any]]]  # Flexível para diferentes tipos

class SincronizacaoResponse(BaseModel):
    """Response da sincronização"""
    sucesso: bool
    usuario: str
    timestamp_servidor: datetime
    resumo: Dict[str, int]
    detalhes: List[str]
    erros: List[str]
    sync_id: int

class StatusSincronizacao(BaseModel):
    """Status atual da sincronização de um usuário"""
    usuario: str
    ultima_sincronizacao: Optional[datetime]
    total_sincronizacoes: int
    total_registros_sincronizados: int
    status_ultima_sync: str
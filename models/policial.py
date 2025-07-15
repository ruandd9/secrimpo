from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, validates
from .base import Base

class Policial(Base):
    __tablename__ = 'policial'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    graduacao = Column(String, nullable=False)
    unidade = Column(String, nullable=False)

    # Relacionamentos
    ocorrencias_condutor = relationship('Ocorrencia', back_populates='policial_condutor', cascade="all, delete-orphan")
    itens_apreendidos = relationship('ItemApreendido', back_populates='policial', cascade="all, delete-orphan")

    @validates('matricula')
    def validate_matricula(self, key, value):
        assert value.isalnum(), "A matrícula deve ser alfanumérica."
        return value

    def __repr__(self):
        return f"<Policial(nome={self.nome}, matricula={self.matricula})>"

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'matricula': self.matricula,
            'graduacao': self.graduacao,
            'unidade': self.unidade
        } 
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, validates
from .base import Base

class Proprietario(Base):
    __tablename__ = 'proprietario'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    documento = Column(String, nullable=False)

    itens_apreendidos = relationship('ItemApreendido', back_populates='proprietario', cascade="all, delete-orphan")

    @validates('documento')
    def validate_documento(self, key, value):
        assert len(value) >= 5, "Documento deve ter pelo menos 5 caracteres."
        return value

    def __repr__(self):
        return f"<Proprietario(nome={self.nome}, documento={self.documento})>"

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'documento': self.documento
        } 
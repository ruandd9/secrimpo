from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, validates
from .base import Base

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
    itens_apreendidos = relationship('ItemApreendido', back_populates='ocorrencia', cascade="all, delete-orphan")

    @validates('data_apreensao')
    def validate_data_apreensao(self, key, value):
        assert value is not None, "Data de apreensão é obrigatória."
        return value

    def __repr__(self):
        return f"<Ocorrencia(numero_genesis={self.numero_genesis}, data_apreensao={self.data_apreensao})>"

    def to_dict(self):
        return {
            'id': self.id,
            'numero_genesis': self.numero_genesis,
            'unidade_fato': self.unidade_fato,
            'data_apreensao': str(self.data_apreensao),
            'lei_infringida': self.lei_infringida,
            'artigo': self.artigo,
            'policial_condutor_id': self.policial_condutor_id
        } 
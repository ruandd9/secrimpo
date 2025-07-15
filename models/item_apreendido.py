from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from .base import Base

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

    @validates('quantidade')
    def validate_quantidade(self, key, value):
        assert value > 0, "Quantidade deve ser maior que zero."
        return value

    def __repr__(self):
        return f"<ItemApreendido(especie={self.especie}, item={self.item}, quantidade={self.quantidade})>"

    def to_dict(self):
        return {
            'id': self.id,
            'especie': self.especie,
            'item': self.item,
            'quantidade': self.quantidade,
            'descricao_detalhada': self.descricao_detalhada,
            'ocorrencia_id': self.ocorrencia_id,
            'proprietario_id': self.proprietario_id,
            'policial_id': self.policial_id
        } 
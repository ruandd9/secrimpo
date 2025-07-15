from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from secrimpo.models.ocorrencia import Base as OcorrenciaBase
from secrimpo.models.policial import Base as PolicialBase
from secrimpo.models.proprietario import Base as ProprietarioBase
from secrimpo.models.item_apreendido import Base as ItemApreendidoBase

# Caminho do banco de dados SQLite
DATABASE_URL = "sqlite:///secrimpo.db"

# Cria o engine
engine = create_engine(DATABASE_URL, echo=True)

# Cria uma sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para criar as tabelas no banco
def init_db():
    # Como todos os modelos usam o mesmo Base, basta chamar uma vez
    from secrimpo.models.ocorrencia import Base
    Base.metadata.create_all(bind=engine)

# Exemplo de uso
if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado e tabelas criadas!") 
#MODELO ORM

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SellerModel(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    celular = Column(String(20), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    status = Column(String(20), default="Inativo")
    codigo_ativacao = Column(String(10), nullable=True)

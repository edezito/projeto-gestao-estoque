from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.Infrastructure.seller import Base

DATABASE_URL = "sqlite:///./mercado.db"  # ou PostgreSQL/MySQL se preferir

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar as tabelas
Base.metadata.create_all(bind=engine)

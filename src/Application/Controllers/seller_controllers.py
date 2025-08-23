#para as rotas do seller (cadastro, ativação, login).

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Application.Service.seller_service import cadastrar_seller, ativar_seller
from src.Config.data_base import SessionLocal
from src.Domain.seller import Seller

router = APIRouter(prefix="/seller", tags=["Seller"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/cadastro")
def criar_seller(seller: Seller, db: Session = Depends(get_db)):
    novo = cadastrar_seller(db, seller)
    return {"message": "Cadastro realizado. Código enviado via WhatsApp.", "seller_id": novo.id}

@router.post("/ativar")
def ativar(cnpj: str, codigo: str, db: Session = Depends(get_db)):
    sucesso = ativar_seller(db, cnpj, codigo)
    if sucesso:
        return {"message": "Conta ativada com sucesso."}
    raise HTTPException(status_code=400, detail="Código inválido ou CNPJ não encontrado.")

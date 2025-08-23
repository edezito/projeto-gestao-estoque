import random
from sqlalchemy.orm import Session
from src.Infrastructure.seller import SellerModel
from src.Domain.seller import Seller

#para hash de senha 
from passlib.hash import bcrypt

#exemplo Twilio (mock, só substituir os bag pra testar)
from twilio.rest import Client

TWILIO_SID = "SEU_SID"
TWILIO_TOKEN = "SEU_TOKEN"
TWILIO_PHONE = "+55SEUNUMERO"

def enviar_codigo_whatsapp(numero: str, codigo: str):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(
            body=f"Seu código de ativação é: {codigo}",
            from_=f"whatsapp:{TWILIO_PHONE}",
            to=f"whatsapp:{numero}"
        )
        return True
    except Exception as e:
        print("Erro ao enviar WhatsApp:", e)
        return False

def cadastrar_seller(db: Session, seller: Seller):
    #código de ativação
    codigo = str(random.randint(1000, 9999))

    novo = SellerModel(
        nome=seller.nome,
        cnpj=seller.cnpj,
        email=seller.email,
        celular=seller.celular,
        senha=bcrypt.hash(seller.senha),
        status="Inativo",
        codigo_ativacao=codigo
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    #código pro wpp
    enviar_codigo_whatsapp(seller.celular, codigo)

    return novo

def ativar_seller(db: Session, cnpj: str, codigo: str):
    seller = db.query(SellerModel).filter(SellerModel.cnpj == cnpj).first()
    if seller and seller.codigo_ativacao == codigo:
        seller.status = "Ativo"
        seller.codigo_ativacao = None
        db.commit()
        return True
    return False

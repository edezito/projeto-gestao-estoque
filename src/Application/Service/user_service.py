import random
from passlib.hash import bcrypt
from src.Domain.user import UserDomain
from src.Infrastructure.Model.user import UserModel
from src.Infrastructure.External.twilio_service import TwilioService
from src.Config import db

class UserService:
    def __init__(self):
        self.twilio_service = TwilioService()

    def create_user(self, nome: str, cnpj: str, email: str, celular: str, senha: str) -> UserDomain:
        #ve se já existe usuário com CNPJ ou e-mail
        existing_user = UserModel.query.filter(
            (UserModel.cnpj == cnpj) | (UserModel.email == email)
        ).first()
        
        if existing_user:
            raise ValueError("CNPJ ou e-mail já cadastrado")

        #código de ativação e o hash da senha
        codigo = f"{random.randint(1000, 9999)}"
        senha_hash = bcrypt.hash(senha)

        #model pra persitencia
        user_model = UserModel(
            nome=nome,
            cnpj=cnpj,
            email=email,
            celular=celular,
            senha=senha_hash,
            status="Inativo",
            codigo_ativacao=codigo,
        )

        #persiste no bd
        db.session.add(user_model)
        db.session.commit()

        #código wpp
        self.twilio_service.send_whatsapp_code(user_model.celular, codigo)

        #cria e retorna dominio
        return UserDomain(
            id=user_model.id,
            nome=user_model.nome,
            cnpj=user_model.cnpj,
            email=user_model.email,
            celular=user_model.celular,
            senha=user_model.senha,
            status=user_model.status,
            codigo_ativacao=user_model.codigo_ativacao
        )

    def activate_user(self, cnpj: str, codigo: str) -> bool:
        user = UserModel.query.filter_by(cnpj=cnpj).first()
        
        if user and user.codigo_ativacao == codigo:
            user.status = "Ativo"
            user.codigo_ativacao = None
            db.session.commit()
            return True
        
        return False
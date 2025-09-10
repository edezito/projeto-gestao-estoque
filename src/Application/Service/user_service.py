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

        user_model = UserModel(
            nome=nome,
            cnpj=cnpj,
            email=email,
            celular=celular,
            senha=senha_hash,
            status="Inativo",
            codigo_ativacao=codigo,
        )

        db.session.add(user_model)
        db.session.commit()

        #código pro wpp
        self.twilio_service.send_whatsapp_code(user_model.celular, codigo)

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

    def authenticate_user(self, login_identifier: str, senha: str) -> UserDomain | None:
        """Autentica usuário pelo CNPJ ou e-mail e senha"""
        user_model = UserModel.query.filter(
            (UserModel.cnpj == login_identifier) | (UserModel.email == login_identifier)
        ).first()

        if not user_model or user_model.status != "Ativo":
            return None

        if bcrypt.verify(senha, user_model.senha):
            return UserDomain(
                id=user_model.id,
                nome=user_model.nome,
                cnpj=user_model.cnpj,
                email=user_model.email,
                celular=user_model.celular,
                senha=user_model.senha,
                status=user_model.status
            )
        
        return None
    
    def get_user_by_id(self, user_id: int) -> UserDomain | None:
        user = UserModel.query.get(user_id)
        if not user:
            return None
        return UserDomain(
            id=user.id,
            nome=user.nome,
            cnpj=user.cnpj,
            email=user.email,
            celular=user.celular,
            senha=user.senha,
            status=user.status
        )

    def update_user(self, user_id: int, dados: dict) -> UserDomain | None:
        user = UserModel.query.get(user_id)
        if not user:
            return None

        #atualiza só os campos recebidos
        user.nome = dados.get("nome", user.nome)
        user.email = dados.get("email", user.email)
        user.celular = dados.get("celular", user.celular)

        db.session.commit()

        return UserDomain(
            id=user.id,
            nome=user.nome,
            cnpj=user.cnpj,
            email=user.email,
            celular=user.celular,
            senha=user.senha,
            status=user.status
        )

    def delete_user(self, user_id: int) -> bool:
        user = UserModel.query.get(user_id)
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True


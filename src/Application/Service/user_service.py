import random
from passlib.hash import bcrypt
from src.Domain.user import UserDomain
from src.Domain.user_data import UserData, preparar_dados_usuario
from src.Infrastructure.Model.user import UserModel
from src.Infrastructure.External.twilio_service import TwilioService
from src.Config import db

class UserService:
    def __init__(self):
        self.twilio_service = TwilioService()

class UserService:
    def __init__(self):
        self.twilio_service = TwilioService()

    def create_user(self, user_data: UserData) -> UserDomain:
        # Verifica duplicidade
        existing_user = UserModel.query.filter(
            (UserModel.cnpj == user_data.cnpj) | (UserModel.email == user_data.email)
        ).first()
        if existing_user:
            raise ValueError("CNPJ ou e-mail já cadastrado")

        dados = preparar_dados_usuario(user_data)

        user_model = UserModel(**dados)
        db.session.add(user_model)
        db.session.commit()

        # Envia código WhatsApp
        try:
            self.twilio_service.send_whatsapp_code(user_model.celular, dados["codigo_ativacao"])
        except Exception as e:
            print(f"AVISO: Usuário {user_model.email} criado, mas falha ao enviar código: {e}")

        return UserDomain(
            id=user_model.id,
            nome=user_model.nome,
            cnpj=user_model.cnpj,
            email=user_model.email,
            celular=user_model.celular,
            senha=user_model.senha,
            status=user_model.status,
            codigo_ativacao=dados["codigo_ativacao"],
        )

    def activate_user(self, cnpj: str, codigo: str) -> bool:
        user = UserModel.query.filter_by(cnpj=cnpj).first()
        
        if user and user.codigo_ativacao == codigo and user.status == "Inativo":
            user.status = "Ativo"
            user.codigo_ativacao = None
            db.session.commit()
            return True
        
        return False

    def authenticate_user(self, login_identifier: str, senha: str) -> UserDomain | None:
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

        # Atualiza só os campos recebidos
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

    def delete_user(self, user_id):
        user = self.session.query(UserDomain).filter_by(id=user_id).first()
        if not user:
            return False
        user.status = "Inativo"   # <- inativando em vez de excluir
        self.session.commit()
        return True
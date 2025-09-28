import random
from passlib.hash import bcrypt
from src.Domain.user import UserDomain
from src.Infrastructure.Model.user import UserModel
from src.Infrastructure.External.twilio_service import TwilioService
from src.Config import db

class UserService:
    def __init__(self):
        self.twilio_service = TwilioService()

    def create_user(self, **kwargs) -> UserDomain:
        required_fields = ["nome", "cnpj", "email", "celular", "senha"]
        missing_fields = [f for f in required_fields if f not in kwargs]
        if missing_fields:
            raise ValueError(f"Campos obrigatórios faltando: {', '.join(missing_fields)}")

        nome = kwargs["nome"]
        cnpj = kwargs["cnpj"]
        email = kwargs["email"]
        celular = kwargs["celular"]
        senha = kwargs["senha"]

        # Verifica duplicidade
        existing_user = UserModel.query.filter(
            (UserModel.cnpj == cnpj) | (UserModel.email == email)
        ).first()
        if existing_user:
            raise ValueError("CNPJ ou e-mail já cadastrado")

        # Hash da senha
        try:
            senha_hash = bcrypt.hash(senha)
        except Exception as e:
            raise ValueError(f"Erro ao gerar hash da senha: {e}")

        codigo = f"{random.randint(1000, 9999)}"

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

        # Envia código WhatsApp
        try:
            self.twilio_service.send_whatsapp_code(user_model.celular, codigo)
        except Exception as e:
            print(f"AVISO: Usuário {email} criado, mas falha ao enviar código via Twilio: {e}")

        return UserDomain(
            id=user_model.id,
            nome=user_model.nome,
            cnpj=user_model.cnpj,
            email=user_model.email,
            celular=user_model.celular,
            senha=user_model.senha,
            status=user_model.status
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

    def inative_user(self, user_id: int) -> bool:
        try:
            user = UserModel.query.get(user_id)
            if not user:
                return False

            user.status = "Inativo"
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao inativar usuário no service: {e}")
            return False
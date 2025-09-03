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
        existing_user = UserModel.query.filter(
            (UserModel.cnpj == cnpj) | (UserModel.email == email)
        ).first()
        
        if existing_user:
            raise ValueError("CNPJ ou e-mail já cadastrado")

        # Gera o código de ativação e o hash da senha
        codigo = f"{random.randint(1000, 9999)}"
        senha_hash = bcrypt.hash(senha)

        # Cria o modelo para persistência
        user_model = UserModel(
            nome=nome,
            cnpj=cnpj,
            email=email,
            celular=celular,
            senha=senha_hash,
            status="Inativo",
            codigo_ativacao=codigo,
        )

        # Persiste no banco
        db.session.add(user_model)
        db.session.commit()

        # Envia código via WhatsApp
        self.twilio_service.send_whatsapp_code(user_model.celular, codigo)

        # Cria e retorna o domínio
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

    # MÉTODO ADICIONADO PARA O PASSO 1
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
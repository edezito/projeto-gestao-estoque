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
        # Verifica duplicidade
        existing_user = UserModel.query.filter(
            (UserModel.cnpj == cnpj) | (UserModel.email == email)
        ).first()
        
        if existing_user:
            raise ValueError("CNPJ ou e-mail já cadastrado")

        # Gera hash da senha (pode falhar se bcrypt não estiver instalado corretamente)
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
        db.session.commit()  # garante que user_model.id seja gerado

        # Envia código via WhatsApp sem quebrar o cadastro
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
                status=user_model.status
            )
        
        return None


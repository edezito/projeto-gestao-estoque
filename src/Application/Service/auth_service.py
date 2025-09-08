import datetime
import os
import jwt
from functools import wraps
from flask import request, jsonify
from src.Infrastructure.Model.user import UserModel
from src.Application.Service.user_service import UserService

class AuthService:
    def __init__(self):
        self.user_service = UserService()

    def authenticate(self, login_identifier: str, senha: str):
        """
        Método central para autenticação.
        Verifica as credenciais e, se válidas, gera o token JWT.
        Retorna (token, None) em caso de sucesso ou (None, error_message) em caso de falha.
        """

        user = self.user_service.authenticate_user(login_identifier, senha)

        if not user:
            return None, "Credenciais inválidas ou conta inativa"
        try:
            token = self._generate_jwt(user)
            return token, None
        except ValueError as e:
            print(f"Erro de configuração JWT: {e}")
            return None, "Erro de configuração no servidor."
        except Exception as e:
            print(f"Erro ao gerar JWT: {e}")
            return None, "Falha ao gerar token de autenticação."

    def _generate_jwt(self, user):
        """Gera um token JWT para um objeto UserDomain."""
        secret = os.environ.get("SENHA_JWT")
        if not secret:
            raise ValueError("SENHA_JWT não configurada no ambiente")
        
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)
        }
        return jwt.encode(payload, secret, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token é obrigatório"}), 401

        try:
            secret = os.environ.get("SENHA_JWT")
            if not secret:
                return jsonify({"message": "JWT secret não definida"}), 500

            data = jwt.decode(token, secret, algorithms=["HS256"])
            from src.Infrastructure.Model.user import UserModel
            current_user = UserModel.query.filter_by(id=data.get("user_id")).first()

            if not current_user:
                return jsonify({"message": "Usuário do token não encontrado"}), 401
            if current_user.status != "Ativo":
                return jsonify({"message": "Usuário inativo"}), 403

            kwargs['current_user'] = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token inválido"}), 401
        except Exception as e:
            print(f"Erro inesperado no token_required: {e}")
            return jsonify({"message": "Erro interno ao validar token"}), 500

        return f(*args, **kwargs)

    return decorated

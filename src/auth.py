import datetime
import os
import jwt
from functools import wraps
from flask import request, jsonify
from passlib.hash import bcrypt
from src.Infrastructure.Model.user import UserModel


class AuthService:
    def authenticate(self, login_identifier: str, senha: str):
        # Permite login por e-mail ou CNPJ
        user = UserModel.query.filter(
            (UserModel.email == login_identifier) | (UserModel.cnpj == login_identifier)
        ).first()

        if not user:
            return None, "Usuário não encontrado"

        if user.status != "Ativo":
            return None, "Usuário inativo"

        if not bcrypt.verify(senha, user.senha):
            return None, "Senha incorreta"

        token = self._generate_jwt(user)
        return token, None

    def _generate_jwt(self, user):
        """Aceita tanto UserModel quanto UserDomain"""
        secret = os.environ.get("SENHA_JWT")
        if not secret:
            raise ValueError("SENHA_JWT não configurada no ambiente")
        
        # Extrai os dados do usuário independentemente do tipo
        user_id = user.id if hasattr(user, 'id') else getattr(user, 'id', None)
        email = user.email if hasattr(user, 'email') else getattr(user, 'email', None)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
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
                return jsonify({"message": "Usuário não encontrado"}), 401
            if current_user.status != "Ativo":
                return jsonify({"message": "Usuário inativo"}), 403

            # Adiciona current_user aos kwargs
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
import datetime
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from passlib.hash import bcrypt
from src.Infrastructure.Model.user import UserModel

class AuthService:
    def authenticate(self, email: str, senha: str):
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            return None, "Usuário não encontrado"
        if user.status != "Ativo":
            return None, "Usuário inativo"
        if not bcrypt.verify(senha, user.senha):
            return None, "Senha incorreta"
        token = self._generate_jwt(user)
        return token, None
    
    def _generate_jwt(self, user):
        payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }
        secret = current_app.config.get("SECRET_KEY", "uma_chave_secreta")
        return jwt.encode(payload, secret, algorithm="HS256")
    
    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            #ostokens tem q vir no header authorization: Bearer <token>
            if "Authorization" in request.headers:
                auth_header = request.headers["Authorization"]
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
            if not token:
                return jsonify({"message": "Token é obrigatório"}), 401

            try:
                secret = current_app.config.get("SECRET_KEY", "uma_chave_secreta") #configurar pro arquivo env dps (get.env)
                data = jwt.decode(token, secret, algorithms=["HS256"])
                current_user = UserModel.query.filter_by(id=data["user_id"]).first()
                if not current_user:
                    return jsonify({"message": "Usuário não encontrado"}), 401
                if current_user.status != "Ativo":
                    return jsonify({"message": "Usuário inativo"}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Token inválido"}), 401

            return f(current_user, *args, **kwargs)
        return decorated

from flask import request, jsonify, Blueprint
from src.Application.Service.user_service import UserService
from src.auth import AuthService, token_required
import jwt
import datetime
import os


class UserController:
    def __init__(self):
        self.user_service = UserService()
        self.auth_service = AuthService()
        self.blueprint = Blueprint('user', __name__)
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/register', 'register', self.register_user, methods=['POST'])
        self.blueprint.add_url_rule('/activate', 'activate', self.activate_user, methods=['POST'])
        self.blueprint.add_url_rule('/login', 'login', self.login, methods=['POST'])
        self.blueprint.add_url_rule('/me', 'get_meus_dados', self.get_meus_dados, methods=['GET'])

    def register_user(self):
        try:
            data = request.get_json() or {}
            required_fields = ["nome", "cnpj", "email", "celular", "senha"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(missing_fields)}"}), 400

            user = self.user_service.create_user(
                nome=data["nome"], cnpj=data["cnpj"], email=data["email"],
                celular=data["celular"], senha=data["senha"]
            )
            return jsonify({"mensagem": "Cadastro realizado. Código enviado via WhatsApp.", "user_id": user.id}), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 409
        except Exception as e:
            print(f"Erro interno: {e}")
            return jsonify({"erro": "Erro interno ao cadastrar usuário."}), 500

    def activate_user(self):
        try:
            data = request.get_json() or {}
            
            if not data.get("cnpj") or not data.get("codigo"):
                return jsonify({"erro": "CNPJ e código são obrigatórios"}), 400

            success = self.user_service.activate_user(data["cnpj"], data["codigo"])
            
            if success:
                return jsonify({"mensagem": "Conta ativada com sucesso."}), 200
            else:
                return jsonify({"erro": "Código inválido ou CNPJ não encontrado."}), 400
        except Exception as e:
            print(f"Erro interno: {e}")
            return jsonify({"erro": "Erro interno ao ativar a conta."}), 500

    def login(self):
        try:
            data = request.get_json(silent=True) or {}
            login_identifier = data.get("login")
            senha = data.get("senha")

            if not login_identifier or not senha:
                return jsonify({"erro": "Login e senha são obrigatórios"}), 400

            # Autentica usuário usando o UserService
            user = self.user_service.authenticate_user(login_identifier, senha)
            if not user:
                return jsonify({"erro": "Credenciais inválidas ou conta inativa"}), 401

            # Geração de token JWT - agora funciona com UserDomain
            try:
                token = self.auth_service._generate_jwt(user)
            except ValueError as e:
                return jsonify({"erro": str(e)}), 500
            except Exception as jwt_err:
                print(f"Erro ao gerar JWT: {jwt_err}")
                return jsonify({"erro": "Falha ao gerar token de autenticação."}), 500

            return jsonify({
                "mensagem": "Login bem-sucedido!",
                "token": token
            }), 200

        except Exception as e:
            print(f"Erro interno no login: {e}")
            return jsonify({"erro": "Erro interno ao tentar fazer login."}), 500


    @token_required
    def get_meus_dados(self, current_user):
        try:
            return jsonify({
                "mensagem": "Acesso à rota protegida concedido com sucesso!",
                "usuario": {
                    "id": current_user.id,
                    "nome": current_user.nome,
                    "email": current_user.email,
                    "status": current_user.status,
                    "cnpj": current_user.cnpj,
                    "celular": current_user.celular
                }
            }), 200
        except Exception as e:
            print(f"Erro em get_meus_dados: {e}")
            return jsonify({"erro": "Erro interno ao buscar dados do usuário"}), 500

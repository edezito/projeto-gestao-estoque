# Arquivo: src/Application/Controllers/user_controller.py

from flask import request, jsonify, Blueprint
from src.Service.user_service import UserService # Corrigido: o caminho correto provavelmente não tem 'Application'
import jwt
import datetime
import os

# --- PASSO 4 Início ---
# 1. IMPORTAR O DECORATOR
from src.Application.Decorators.auth import token_required
# --- PASSO 4 Fim ---

class UserController:
    def __init__(self):
        self.user_service = UserService()
        self.blueprint = Blueprint('user', __name__)
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/register', 'register', self.register_user, methods=['POST'])
        self.blueprint.add_url_rule('/activate', 'activate', self.activate_user, methods=['POST'])
        self.blueprint.add_url_rule('/login', 'login', self.login, methods=['POST'])
        
        # --- PASSO 4 Início ---
        # 2. REGISTRAR A NOVA ROTA PROTEGIDA
        self.blueprint.add_url_rule('/me', 'get_meus_dados', self.get_meus_dados, methods=['GET'])
        # --- PASSO 4 Fim ---

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
            data = request.get_json() or {}
            identifier = data.get("identifier")
            password = data.get("senha")

            if not identifier or not password:
                return jsonify({"erro": "Identificador (CNPJ/e-mail) e senha são obrigatórios"}), 400

            authenticated_user = self.user_service.authenticate_user(
                login_identifier=identifier,
                senha=password
            )

            if not authenticated_user:
                return jsonify({"erro": "Credenciais inválidas ou usuário inativo."}), 401

            payload = {
                'id': authenticated_user.id,
                'nome': authenticated_user.nome,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            secret_key = os.getenv('JWT_SECRET')
            token = jwt.encode(payload, secret_key, algorithm='HS256')

            return jsonify({"mensagem": "Login bem-sucedido!", "token": token}), 200
        except Exception as e:
            print(f"Erro interno no login: {e}")
            return jsonify({"erro": "Erro interno ao tentar fazer login."}), 500

    # 3. CRIAR O MÉTODO PROTEGIDO PELO DECORATOR
    @token_required
    def get_meus_dados(self, current_user):
        """
        Endpoint protegido. Só pode ser acessado com um token JWT válido.
        O decorator injeta os dados do token no parâmetro 'current_user'.
        """
        return jsonify({
            "mensagem": f"Acesso à rota protegida concedido com sucesso!",
            "dados_do_usuario_no_token": current_user
        }), 200

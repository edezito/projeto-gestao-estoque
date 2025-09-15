from flask import request, jsonify, Blueprint
from src.Application.Service.user_service import UserService
from src.auth import AuthService, token_required

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
        # Mantendo rota protegida
        self.blueprint.add_url_rule('/me', 'me', self.get_meus_dados, methods=['GET'])
        # Novas rotas pro CRUD
        self.blueprint.add_url_rule('/<int:user_id>', 'get_user', self.get_user_by_id, methods=['GET'])
        self.blueprint.add_url_rule('/<int:user_id>', 'update_user', self.update_user, methods=['PUT'])
        self.blueprint.add_url_rule('/<int:user_id>', 'delete_user', self.delete_user, methods=['DELETE'])

    def register_user(self):
        try:
            data = request.get_json() or {}
            required_fields = ["nome", "cnpj", "email", "celular", "senha"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(missing_fields)}"}), 400

            user = self.user_service.create_user(
                nome=data["nome"],
                cnpj=data["cnpj"],
                email=data["email"],
                celular=data["celular"],
                senha=data["senha"]
            )

            return jsonify({
                "mensagem": "Cadastro realizado. Código enviado via WhatsApp.",
                "user_id": getattr(user, "id", None)
            }), 201

        except ValueError as e:
            return jsonify({"erro": str(e)}), 409
        except Exception as e:
            import traceback
            traceback.print_exc()
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

            # autenticação centralizada no AuthService
            token, error_message = self.auth_service.authenticate(login_identifier, senha)
            if error_message:
                return jsonify({"erro": error_message}), 401

            return jsonify({"mensagem": "Login bem-sucedido!", "token": token}), 200

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
        
    @token_required
    def get_user_by_id(self, current_user, user_id):
        try:
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return jsonify({"erro": "Usuário não encontrado"}), 404
            return jsonify(user.__dict__), 200
        except Exception as e:
            print(f"Erro em get_user_by_id: {e}")
            return jsonify({"erro": "Erro interno ao buscar usuário"}), 500

    @token_required
    def update_user(self, current_user, user_id):
        try:
            dados = request.json or {}
            user = self.user_service.update_user(user_id, dados)
            if not user:
                return jsonify({"erro": "Usuário não encontrado"}), 404
            return jsonify(user.__dict__), 200
        except Exception as e:
            print(f"Erro em update_user: {e}")
            return jsonify({"erro": "Erro interno ao atualizar usuário"}), 500

    @token_required
    def delete_user(self, current_user, user_id):
        try:
            sucesso = self.user_service.delete_user(user_id)
            if not sucesso:
                return jsonify({"erro": "Usuário não encontrado"}), 404
            return jsonify({"mensagem": "Usuário deletado com sucesso"}), 200
        except Exception as e:
            print(f"Erro em delete_user: {e}")
            return jsonify({"erro": "Erro interno ao deletar usuário"}), 500

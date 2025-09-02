from flask import request, jsonify, Blueprint
from src.Application.Service.user_service import UserService
from src.Application.Service.auth_service import AuthService

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
        self.blueprint.add_url_rule('/me', 'me', self.get_profile, methods=['GET']) #Rota protegida

    def register_user(self):
        try:
            data = request.get_json() or {}
            #validando os campos obrigatórios
            required_fields = ["nome", "cnpj", "email", "celular", "senha"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return jsonify({
                    "erro": f"Campos obrigatórios faltando: {', '.join(missing_fields)}"
                }), 400

            # Cria o usuário
            user = self.user_service.create_user(
                nome=data["nome"],
                cnpj=data["cnpj"],
                email=data["email"],
                celular=data["celular"],
                senha=data["senha"]
            )

            return jsonify({
                "mensagem": "Cadastro realizado. Código enviado via WhatsApp.",
                "user_id": user.id
            }), 201

        except ValueError as e:
            return jsonify({"erro": str(e)}), 409
        except Exception as e:
            print(f"Erro interno: {e}")
            return jsonify({"erro": "Erro interno ao cadastrar usuário."}), 500

    def activate_user(self):
        try:
            data = request.get_json() or {}
            
            if not data.get("cnpj") or not data.get("codigo"):
                return jsonify({
                    "erro": "CNPJ e código são obrigatórios"
                }), 400

            success = self.user_service.activate_user(data["cnpj"], data["codigo"])
            
            if success:
                return jsonify({
                    "mensagem": "Conta ativada com sucesso."
                }), 200
            else:
                return jsonify({
                    "erro": "Código inválido ou CNPJ não encontrado."
                }), 400

        except Exception as e:
            print(f"Erro interno: {e}")
            return jsonify({
                "erro": "Erro interno ao ativar a conta."
            }), 500
        
    def login(self):
        try:
            data = request.get_json() or {}
            email = data.get("email")
            senha = data.get("senha")
            if not email or not senha:
                return jsonify({"erro": "Email e senha são obrigatórios"}), 400

            token, error = self.auth_service.authenticate(email, senha)
            if error:
                return jsonify({"erro": error}), 401

            return jsonify({"token": token}), 200
        except Exception as e:
            print(f"Erro interno: {e}")
            return jsonify({"erro": "Erro interno ao autenticar."}), 500
        
    @AuthService.token_required
    def get_profile(self, current_user):  #fznd exemplo de rota protegida
        try:
            return jsonify({
                "id": current_user.id,
                "nome": current_user.nome,
                "email": current_user.email,
                "status": current_user.status
            }), 200
        except Exception as e:
            print(f"Erro interno: {e}")
            return jsonify({"erro": "Erro ao buscar dados do perfil."}), 500
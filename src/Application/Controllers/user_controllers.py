from flask import request, jsonify, Blueprint
from src.Application.Service.user_service import UserService

class UserController:
    def __init__(self):
        self.user_service = UserService()
        self.blueprint = Blueprint('user', __name__)
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/register', 'register', self.register_user, methods=['POST'])
        self.blueprint.add_url_rule('/activate', 'activate', self.activate_user, methods=['POST'])

    def register_user(self):
        try:
            data = request.get_json() or {}
            
            # Validação dos campos obrigatórios
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
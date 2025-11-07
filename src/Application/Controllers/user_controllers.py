from flask import request, jsonify, Blueprint
from src.Application.Service.user_service import UserService
from src.auth import AuthService, token_required
from werkzeug.exceptions import BadRequest
import json

class UserController:
    def __init__(self):
        self.blueprint = Blueprint('user', __name__, url_prefix='/api/users')
        self.user_service = UserService()
        self.auth_service = AuthService()
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('/register', 'register', self.register_user, methods=['POST', 'OPTIONS'])
        self.blueprint.add_url_rule('/activate', 'activate', self.activate_user, methods=['POST', 'OPTIONS'])
        self.blueprint.add_url_rule('/login', 'login', self.login, methods=['POST', 'OPTIONS'])
        self.blueprint.add_url_rule('/<int:user_id>', 'get_user_by_id', self.get_profile_by_id, methods=['GET', 'OPTIONS'])
        self.blueprint.add_url_rule('/<int:user_id>', 'update_user', self.update_user, methods=['PUT', 'OPTIONS'])
        self.blueprint.add_url_rule('/<int:user_id>/inactivate', 'inactivate_user', self.inactivate_user, methods=['POST', 'OPTIONS'])

    def register_user(self):
        try:
            # Tenta pegar o JSON de forma segura
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({"erro": "JSON inválido"}), 400
                
            required_fields = ["nome", "cnpj", "email", "celular", "senha"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return jsonify({
                    "erro": f"Campos obrigatórios faltando: {', '.join(missing_fields)}"
                }), 400

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
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({"erro": "JSON inválido"}), 400
            
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
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({"erro": "JSON inválido"}), 400
                
            login_identifier = data.get("login")
            senha = data.get("senha")

            if not login_identifier or not senha:
                return jsonify({"erro": "Login e senha são obrigatórios"}), 400
                
            token, error_message = self.auth_service.authenticate(login_identifier, senha)

            if error_message:
                return jsonify({"erro": error_message}), 401

            return jsonify({
                "mensagem": "Login bem-sucedido!",
                "token": token
            }), 200

        except Exception as e:
            print(f"Erro interno no login: {e}")
            return jsonify({"erro": "Erro interno ao tentar fazer login."}), 500

    @token_required
    def get_profile(self, current_user):
        try:
            return jsonify({
                "id": current_user.id,
                "nome": current_user.nome,
                "email": current_user.email,
                "cnpj": current_user.cnpj,
                "celular": current_user.celular,
                "status": current_user.status
            }), 200
        except Exception as e:
            print(f"Erro interno: {e}")
            return jsonify({"erro": "Erro ao buscar dados do perfil."}), 500
        
    @token_required 
    def get_profile_by_id(self, current_user, user_id):
        """
        Endpoint para buscar o perfil de um usuário pelo ID.
        O 'user_id' virá da URL.
        """
        try:
            # A lógica de serviço deve ser chamada aqui
            user_domain = self.user_service.get_user_by_id(user_id)

            if not user_domain:
                return jsonify({"mensagem": "Usuário não encontrado."}), 404

            # Se precisar de um JSON serializável
            user_data = user_domain.to_dict()
            user_data.pop('senha', None) # Remova a senha do retorno

            return jsonify(user_data), 200

        except Exception as e:
            return jsonify({"mensagem": "Erro interno do servidor", "erro": str(e)}), 500
        
    @token_required
    def update_user(self, current_user, user_id):
        """
        Endpoint para atualizar os dados de um usuário existente.
        """
        try:
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({"mensagem": "JSON inválido"}), 400
                
            if not data:
                return jsonify({"mensagem": "Dados de atualização ausentes no corpo da requisição."}), 400

            # Chamar a lógica de serviço para realizar a atualização
            updated_user_domain = self.user_service.update_user(user_id, data)

            if not updated_user_domain:
                return jsonify({"mensagem": "Usuário não encontrado ou falha na atualização."}), 404

            user_data = updated_user_domain.to_dict()
            user_data.pop('senha', None)

            return jsonify({"mensagem": "Usuário atualizado com sucesso.", "usuario": user_data}), 200

        except ValueError as e:
            return jsonify({"mensagem": str(e)}), 400
        except Exception as e:
            print(f"Erro ao atualizar usuário: {e}")
            return jsonify({"mensagem": "Erro interno do servidor."}), 500
        
    @token_required
    def inactivate_user(self, current_user, user_id):
        """
        Endpoint para inativar um usuário pelo ID.
        """
        try:
            success = self.user_service.inactivate_user_by_id(user_id)

            if success:
                return jsonify({"mensagem": f"Usuário {user_id} inativado com sucesso."}), 200
            else:
                return jsonify({"mensagem": "Usuário não encontrado ou já está inativo."}), 404

        except Exception as e:
            print(f"Erro ao inativar usuário: {e}")
            return jsonify({"mensagem": "Erro interno do servidor."}), 500
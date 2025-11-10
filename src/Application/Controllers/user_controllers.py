from flask import request, jsonify, Blueprint
from src.Application.Service.user_service import UserService
from src.Application.Service.auth_service import AuthService
from src.Application.Service.auth_service import token_required
from flask import current_app


class UserController:
    def __init__(self):
        self.blueprint = Blueprint('user', __name__, url_prefix='/api/users')
        self.user_service = UserService()
        self.auth_service = AuthService()
        self._register_routes()

    def _register_routes(self):
        # ✅ ROTAS PRINCIPAIS - APENAS AS QUE EXISTEM
        self.blueprint.add_url_rule('/register', 'register', self.register_user, methods=['POST'])
        self.blueprint.add_url_rule('/activate', 'activate', self.activate_user, methods=['POST'])
        self.blueprint.add_url_rule('/login', 'login', self.login, methods=['POST'])

        self.blueprint.add_url_rule('/me', 'update_profile', self.update_profile, methods=['PATCH'])
        self.blueprint.add_url_rule('/deactivate', 'deactivate_account', self.deactivate_account, methods=['POST'])

        # ✅ ROTAS DE DEBUG (funcionam)
        self.blueprint.add_url_rule('/list-all', 'list_all_users', self.list_all_users, methods=['GET'])
        self.blueprint.add_url_rule('/get-activation-code/<string:cnpj>', 'get_activation_code', self.get_activation_code, methods=['GET'])

    def register_user(self):
        try:
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
                
            # ✅ AGORA RECEBE 3 VALORES: token, user_data, error_message
            token, user_data, error_message = self.auth_service.authenticate(login_identifier, senha)

            if error_message:
                return jsonify({"erro": error_message}), 401

            # ✅ RETORNA TOKEN E DADOS DO USUÁRIO
            response_data = {
                "mensagem": "Login bem-sucedido!",
                "token": token,
                "user": user_data  # ✅ ADICIONA OS DADOS DO USUÁRIO
            }

            return jsonify(response_data), 200

        except Exception as e:
            print(f"Erro interno no login: {e}")
            return jsonify({"erro": "Erro interno ao tentar fazer login."}), 500

    # ✅ NOVAS ROTAS DE DEBUG
    def list_all_users(self):
        """Lista todos os usuários (para debug)"""
        try:
            from src.Infrastructure.Model.user import UserModel
            users = UserModel.query.all()
            
            result = []
            for user in users:
                result.append({
                    'id': user.id,
                    'nome': user.nome,
                    'cnpj': user.cnpj,
                    'email': user.email,
                    'celular': user.celular,
                    'status': user.status,
                    'codigo_ativacao': user.codigo_ativacao
                })
            
            return jsonify({
                'total': len(result),
                'users': result
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_activation_code(self, cnpj):
        """Busca código de ativação por CNPJ (para debug)"""
        try:
            from src.Infrastructure.Model.user import UserModel
            user = UserModel.query.filter_by(cnpj=cnpj).first()
            
            if user:
                return jsonify({
                    'id': user.id,
                    'nome': user.nome,
                    'cnpj': user.cnpj,
                    'celular': user.celular,
                    'codigo_ativacao': user.codigo_ativacao,
                    'status': user.status
                }), 200
            else:
                return jsonify({'erro': 'Usuário não encontrado'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@token_required
def update_profile(self, current_user):
    try:
        data = request.get_json(silent=True) or {}
        # campos permitidos para atualização via profile
        allowed = {"nome", "email", "celular"}
        payload = {k: v for k, v in data.items() if k in allowed}

        if not payload:
            return jsonify({"erro": "Nenhum campo válido para atualizar."}), 400

        # delega ao service (implementaremos update_user)
        updated_user = self.user_service.update_user(current_user.id, payload)

        # returned user pode ser UserDomain ou dict
        user_out = updated_user.to_dict() if hasattr(updated_user, "to_dict") else updated_user

        return jsonify({"mensagem": "Perfil atualizado.", "user": user_out}), 200

    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Erro update_profile: {e}")
        return jsonify({"erro": "Erro ao atualizar perfil."}), 500


@token_required
def deactivate_account(self, current_user):
    try:
        # delega ao service
        success = self.user_service.inactivate_user_by_id(current_user.id)
        if success:
            return jsonify({"mensagem": "Conta inativada com sucesso."}), 200
        return jsonify({"erro": "Usuário não encontrado ou já inativo."}), 400
    except Exception as e:
        current_app.logger.error(f"Erro deactivate_account: {e}")
        return jsonify({"erro": "Erro ao inativar conta."}), 500

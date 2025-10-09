from flask import request, jsonify, Blueprint
from src.Application.Service.produto_service import ProductService
from src.auth import token_required

class ProductController:
    def __init__(self):
        self.product_service = ProductService()
        self.blueprint = Blueprint('product', __name__, url_prefix='/products')
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('', 'list_create_products', self.list_or_create, methods=['GET', 'POST'])
        self.blueprint.add_url_rule('/<int:product_id>', 'product_details', self.get_product_details, methods=['GET'])
        self.blueprint.add_url_rule('/<int:product_id>', 'update_product', self.update_product, methods=['PUT'])

    # Rota única que gerencia GET e POST
    def list_or_create(self):
        if request.method == 'POST':
            return self.create_product()
        return self.list_products()

    @token_required
    def create_product(self, current_user):
        """Cria um novo produto vinculado ao usuário autenticado."""
        try:
            data = request.get_json() or {}
            required_fields = ["nome", "preco", "quantidade"]
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(missing_fields)}"}), 400

            product = self.product_service.create_product(data, user_id=current_user.id)
            return jsonify(product.to_dict()), 201

        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao cadastrar produto: {e}"}), 500

    @token_required
    def list_products(self, current_user):
        """Lista todos os produtos do usuário autenticado."""
        try:
            products = self.product_service.get_products_by_user(user_id=current_user.id)
            return jsonify([p.to_dict() for p in products]), 200
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao listar produtos: {e}"}), 500

    @token_required
    def get_product_details(self, current_user, product_id):
        """Retorna detalhes de um produto específico do usuário."""
        try:
            product = self.product_service.get_product_by_id_and_user(product_id, user_id=current_user.id)
            if product:
                return jsonify(product.to_dict()), 200
            return jsonify({"erro": "Produto não encontrado ou não pertence a você."}), 404
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao buscar detalhes do produto: {e}"}), 500

    @token_required
    def update_product(self, current_user, product_id):
        """Atualiza um produto, inclusive seu status."""
        try:
            data = request.get_json() or {}
            if not data:
                return jsonify({"erro": "Corpo da requisição não pode ser vazio."}), 400

            updated_product = self.product_service.update_product(
                product_id=product_id,
                user_id=current_user.id,
                data=data
            )

            if updated_product:
                return jsonify(updated_product.to_dict()), 200
            return jsonify({"erro": "Produto não encontrado ou não pertence a você."}), 404

        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao atualizar o produto: {e}"}), 500

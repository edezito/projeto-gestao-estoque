from flask import request, jsonify, Blueprint
from src.Application.Service.produto_service import ProductService
from src.auth import token_required

class ProductController:
    def __init__(self):
        self.product_service = ProductService()
        # O prefixo base do Blueprint deve ser /api/products
        self.blueprint = Blueprint('product', __name__, url_prefix='/api/products') # <<-- ALTERAÇÃO AQUI
        self._register_routes()

    def _register_routes(self):
        self.blueprint.add_url_rule('', 'list_create_products', self.list_or_create, methods=['GET', 'POST', 'OPTIONS'])
        self.blueprint.add_url_rule('/<int:product_id>', 'product_details', self.get_product_details, methods=['GET', 'OPTIONS'])
        self.blueprint.add_url_rule('/<int:product_id>', 'update_product', self.update_product, methods=['PUT', 'OPTIONS'])
        self.blueprint.add_url_rule('/<int:product_id>/inactivate', 'inactivate_product', self.inactivate_product, methods=['PATCH', 'OPTIONS'])
        self.blueprint.add_url_rule('/<int:product_id>', 'delete_product', self.delete_product, methods=['DELETE', 'OPTIONS'])

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
        
    @token_required
    def inactivate_product(self, current_user, product_id):
        """Inativa um produto específico do usuário via PATCH."""
        try:
            inactivated_product = self.product_service.inactivate_product(
                product_id=product_id,
                user_id=current_user.id
            )

            if inactivated_product:
                return jsonify(inactivated_product.to_dict()), 200
            
            # Note: 404 é adequado se não encontra ou não pertence ao usuário
            return jsonify({"erro": "Produto não encontrado ou não pertence a você."}), 404

        except Exception as e:
            return jsonify({"erro": f"Erro interno ao inativar o produto: {e}"}), 500

        
    @token_required # <--- Adicionar este método
    def delete_product(self, current_user, product_id):
        """Exclui um produto específico do usuário."""
        try:
            # Chama o método de serviço para exclusão
            deleted_count = self.product_service.delete_product(
                product_id=product_id,
                user_id=current_user.id
            )

            if deleted_count > 0:
                return jsonify({"message": f"Produto {product_id} excluído com sucesso."}), 200
            
            # 404 se não encontra ou não pertence ao usuário
            return jsonify({"erro": "Produto não encontrado ou não pertence a você."}), 404

        except Exception as e:
            return jsonify({"erro": f"Erro interno ao excluir o produto: {e}"}), 500

from flask import request, jsonify, Blueprint
from src.Application.Service.venda_service import VendaService
from src.auth import token_required

class VendaController:
    def __init__(self):
        self.venda_service = VendaService()
        self.blueprint = Blueprint('venda', __name__, url_prefix='/api/sales')
        self._register_routes()

    def _register_routes(self):
        # ✅ CORRIGIDO: Separar GET e POST em métodos distintos
        self.blueprint.add_url_rule('', 'list_sales', self.list_sales, methods=['GET'])
        self.blueprint.add_url_rule('', 'create_sale', self.create_sale, methods=['POST'])
        self.blueprint.add_url_rule('/<int:sale_id>', 'get_sale', self.get_sale_details, methods=['GET'])
        self.blueprint.add_url_rule('/<int:sale_id>', 'delete_sale', self.delete_sale, methods=['DELETE'])

    @token_required
    def create_sale(self, current_user):
        """
        Cria uma nova venda associada ao seller autenticado.
        """
        try:
            data = request.get_json() or {}
            required_fields = ["produto_id", "quantidade"]
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                return jsonify({"erro": f"Campos obrigatórios faltando: {', '.join(missing_fields)}"}), 400

            # Conversões/validações básicas
            try:
                produto_id = int(data.get("produto_id"))
                quantidade = int(data.get("quantidade"))
            except (TypeError, ValueError):
                return jsonify({"erro": "produto_id e quantidade devem ser números inteiros."}), 400

            if quantidade <= 0:
                return jsonify({"erro": "A quantidade vendida deve ser maior que zero."}), 400

            venda = self.venda_service.create_sale(
                produto_id=produto_id,
                quantidade=quantidade,
                seller_id=current_user.id
            )

            return jsonify(venda.to_dict()), 201

        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao processar a venda: {e}"}), 500

    @token_required
    def list_sales(self, current_user):
        """Lista todas as vendas realizadas pelo seller autenticado."""
        try:
            vendas = self.venda_service.get_sales_by_seller(seller_id=current_user.id)
            return jsonify([v.to_dict() for v in vendas]), 200
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao listar vendas: {e}"}), 500

    @token_required
    def get_sale_details(self, current_user, sale_id):
        """Retorna detalhes de uma venda específica do seller."""
        try:
            venda = self.venda_service.get_sale_by_id_and_seller(sale_id=sale_id, seller_id=current_user.id)
            if venda:
                return jsonify(venda.to_dict()), 200
            return jsonify({"erro": "Venda não encontrada ou não pertence a você."}), 404
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao buscar detalhes da venda: {e}"}), 500

    @token_required
    def delete_sale(self, current_user, sale_id):
        """Exclui uma venda."""
        try:
            deleted_count = self.venda_service.delete_sale(sale_id=sale_id, seller_id=current_user.id)
            if deleted_count > 0:
                return jsonify({"message": f"Venda {sale_id} excluída com sucesso."}), 200
            return jsonify({"erro": "Venda não encontrada ou não pertence a você."}), 404
        except Exception as e:
            return jsonify({"erro": f"Erro interno ao excluir a venda: {e}"}), 500
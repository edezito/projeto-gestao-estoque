from typing import List, Dict, Any, Optional
from src.Domain.produto import ProductDomain
from src.Infrastructure.Model.produtos import ProductModel
from src.Infrastructure.Model.user import UserModel
from src.Config import db

class ProductService:
    def create_product(self, data: Dict[str, Any], user_id: int) -> ProductDomain:
        """Cria um novo produto associado a um usuário."""
        if not UserModel.query.get(user_id):
            raise ValueError("Usuário não encontrado.")

        product_model = ProductModel(
            nome=data.get("nome"),
            preco=float(data.get("preco")),
            quantidade=int(data.get("quantidade")),
            status=data.get("status", "Ativo"),
            imagem=data.get("imagem"),
            user_id=user_id
        )

        db.session.add(product_model)
        db.session.commit()
        return self._map_model_to_domain(product_model)

    def get_products_by_user(self, user_id: int) -> List[ProductDomain]:
        """Lista todos os produtos do usuário."""
        product_models = ProductModel.query.filter_by(user_id=user_id).all()
        return [self._map_model_to_domain(p) for p in product_models]

    def get_product_by_id_and_user(self, product_id: int, user_id: int) -> Optional[ProductDomain]:
        """Busca um produto específico, garantindo que pertence ao usuário."""
        product_model = ProductModel.query.filter_by(id=product_id, user_id=user_id).first()
        if product_model:
            return self._map_model_to_domain(product_model)
        return None

    def update_product(self, product_id: int, user_id: int, data: Dict[str, Any]) -> Optional[ProductDomain]:
        """Atualiza um produto (se pertencer ao usuário)."""
        product_model = ProductModel.query.filter_by(id=product_id, user_id=user_id).first()
        if not product_model:
            return None

        for key, value in data.items():
            if hasattr(product_model, key):
                setattr(product_model, key, value)

        db.session.commit()
        return self._map_model_to_domain(product_model)

    def _map_model_to_domain(self, model: ProductModel) -> ProductDomain:
        """Converte um Model em objeto de Domínio incluindo user_id."""
        return ProductDomain(
            id=model.id,
            nome=model.nome,
            preco=model.preco,
            quantidade=model.quantidade,
            status=model.status,
            imagem=model.imagem,
            user_id=model.user_id
        )

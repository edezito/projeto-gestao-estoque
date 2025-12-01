from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import joinedload 

from src.Domain.venda import VendaDomain 
from src.Infrastructure.Model.vendas import VendaModel
from src.Infrastructure.Model.produtos import ProductModel
from src.Infrastructure.Model.user import UserModel
from src.Config import db


class VendaService:

    def create_sale(self, produto_id: int, quantidade: int, seller_id: int) -> VendaDomain:
        """
        Cria uma venda e atualiza o estoque do produto.
        """
        if quantidade <= 0:
            raise ValueError("A quantidade vendida deve ser maior que zero.")

        session = db.session
        
        # Verifica seller
        user = session.query(UserModel).get(seller_id)
        if not user:
            raise ValueError("Seller (usuário) não encontrado.")

        # Checa se o seller está ativo
        is_user_active = True
        if hasattr(user, "status"):
            is_user_active = (str(getattr(user, "status")).lower() != "inativo")

        if not is_user_active:
            raise ValueError("Seller inativo não pode realizar vendas.")

        try:
            # Busca o produto com lock para evitar race conditions
            produto = session.query(ProductModel).filter_by(id=produto_id).with_for_update().first()
            if not produto:
                raise ValueError("Produto não encontrado.")

            # Verifica se o produto pertence ao seller
            if getattr(produto, "user_id", None) is not None and produto.user_id != seller_id:
                raise ValueError("Você não tem permissão para vender este produto.")

            # Verifica status/atividade do produto
            is_produto_active = True
            if hasattr(produto, "status"):
                is_produto_active = (str(getattr(produto, "status")).lower() == "ativo")

            if not is_produto_active:
                raise ValueError("Produtos inativados não podem ser vendidos.")

            # Verifica estoque
            estoque_atual = getattr(produto, "quantidade", None)
            if estoque_atual is None:
                raise ValueError("Produto não possui informação de estoque.")
            if estoque_atual < quantidade:
                raise ValueError("Estoque insuficiente para realizar a venda.")

            # Preço no momento da venda
            preco_atual = getattr(produto, "preco", None)
            if preco_atual is None:
                raise ValueError("Produto não possui preço definido.")

            # Atualiza estoque
            produto.quantidade = estoque_atual - quantidade
            session.add(produto)

            # Cria o modelVenda
            venda_model = VendaModel(
                produto_id=produto.id,
                quantidade=quantidade,
                preco_vendido=float(preco_atual),
                seller_id=seller_id,
                created_at=datetime.utcnow()
            )

            session.add(venda_model)
            session.commit()

            # Recarrega a venda com os relacionamentos
            venda_completa = session.query(VendaModel).options(
                joinedload(VendaModel.produto)
            ).filter_by(id=venda_model.id).first()
            
            return self._map_model_to_domain(venda_completa)

        except ValueError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro interno ao criar venda: {e}")

    def get_sales_by_seller(self, seller_id: int) -> List[VendaDomain]:
        """Retorna todas as vendas do seller, ordenadas por data (desc)."""
        try:
            vendas = VendaModel.query.options(
                joinedload(VendaModel.produto)
            ).filter_by(
                seller_id=seller_id
            ).order_by(
                VendaModel.created_at.desc()
            ).all()
            
            return [self._map_model_to_domain(v) for v in vendas]
        except Exception as e:
            raise Exception(f"Erro interno ao listar vendas: {e}")

    def get_sale_by_id_and_seller(self, sale_id: int, seller_id: int) -> Optional[VendaDomain]:
        """Retorna uma venda específica se pertencer ao seller."""
        try:
            venda = VendaModel.query.options(
                joinedload(VendaModel.produto)
            ).filter_by(
                id=sale_id, seller_id=seller_id
            ).first()
            
            if not venda:
                return None
            return self._map_model_to_domain(venda)
        except Exception as e:
            raise Exception(f"Erro interno ao buscar venda: {e}")

    def delete_sale(self, sale_id: int, seller_id: int) -> bool:
        """Exclui uma venda específica do seller."""
        session = db.session
        try:
            venda = VendaModel.query.filter_by(id=sale_id, seller_id=seller_id).first()
            if not venda:
                return False

            session.delete(venda)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro interno ao excluir venda: {e}")

    def _map_model_to_domain(self, model: VendaModel) -> VendaDomain:
        """
        Mapeia VendaModel para VendaDomain, incluindo os detalhes do produto.
        """
        produto_details = None
        if model.produto: 
            produto_details = {
                'id': model.produto.id,
                'nome': getattr(model.produto, 'nome', 'N/A'),
                'preco': getattr(model.produto, 'preco', 0.0)
            }

        return VendaDomain(
            id=model.id,
            produto_id=model.produto_id,
            quantidade=model.quantidade,
            preco_vendido=model.preco_vendido,
            seller_id=model.seller_id,
            created_at=model.created_at,
            produto_details=produto_details
        )

    def
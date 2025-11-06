from typing import List, Dict, Any, Optional
from datetime import datetime

from src.Domain.venda import VendaDomain 
from src.Infrastructure.Model.vendas import VendaModel  
from src.Infrastructure.Model.produtos import ProductModel
from src.Infrastructure.Model.user import UserModel
from src.Config import db


class VendaService:
    def __init__(self):
        pass

    def create_sale(self, produto_id: int, quantidade: int, seller_id: int) -> VendaDomain:
        """
        Cria uma venda e atualiza o estoque do produto.
        Lança ValueError quando uma regra de negócio é violada:
          - usuário/seller não encontrado
          - seller inativo
          - produto não encontrado
          - produto não pertence ao seller (regra assumida)
          - produto inativo
          - estoque insuficiente
        Retorna um VendaDomain (mapeado a partir do model criado).
        """
        if quantidade <= 0:
            raise ValueError("A quantidade vendida deve ser maior que zero.")

        # Verifica seller
        user = UserModel.query.get(seller_id)
        if not user:
            raise ValueError("Seller (usuário) não encontrado.")

        # Checa se o seller está ativo (adapta conforme campos reais do seu UserModel)
        is_user_active = True
        if hasattr(user, "ativo"):
            is_user_active = bool(getattr(user, "ativo"))
        elif hasattr(user, "is_active"):
            is_user_active = bool(getattr(user, "is_active"))
        elif hasattr(user, "status"):
            is_user_active = (str(getattr(user, "status")).lower() != "inativo")

        if not is_user_active:
            raise ValueError("Seller inativo não pode realizar vendas.")

        # Transação: buscar produto e atualizar estoque
        session = db.session
        try:
            # Busca o produto (não usamos with_for_update aqui porque você usa SQLAlchemy padrão;
            # se quiser lock em concorrência, adicione .with_for_update() ao query se seu DB suportar)
            produto: ProductModel = session.query(ProductModel).filter_by(id=produto_id).first()
            if not produto:
                raise ValueError("Produto não encontrado.")

            # Verifica se o produto pertence ao seller (ajuste se a regra for diferente)
            if getattr(produto, "user_id", None) is not None and produto.user_id != seller_id:
                raise ValueError("Você não tem permissão para vender este produto.")

            # Verifica status/atividade do produto
            is_produto_active = True
            if hasattr(produto, "status"):
                is_produto_active = (str(getattr(produto, "status")).lower() == "ativo")
            elif hasattr(produto, "ativo"):
                is_produto_active = bool(getattr(produto, "ativo"))

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

            # Atualiza a instância (garantir id etc.)
            session.refresh(venda_model)

            return self._map_model_to_domain(venda_model)

        except ValueError:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro interno ao criar venda: {e}")

    def get_sales_by_seller(self, seller_id: int) -> List[VendaDomain]:
        """Retorna todas as vendas do seller, ordenadas por data (desc)."""
        try:
            vendas = VendaModel.query.filter_by(seller_id=seller_id).order_by(VendaModel.created_at.desc()).all()
            return [self._map_model_to_domain(v) for v in vendas]
        except Exception as e:
            raise Exception(f"Erro interno ao listar vendas: {e}")

    def get_sale_by_id_and_seller(self, sale_id: int, seller_id: int) -> Optional[VendaDomain]:
        """Retorna uma venda específica se pertencer ao seller."""
        try:
            venda = VendaModel.query.filter_by(id=sale_id, seller_id=seller_id).first()
            if not venda:
                return None
            return self._map_model_to_domain(venda)
        except Exception as e:
            raise Exception(f"Erro interno ao buscar venda: {e}")

    def delete_sale(self, sale_id: int, seller_id: int) -> int:
        """
        Exclui uma venda se pertencer ao seller.
        Retorna número de registros excluídos (0 ou 1).
        Observação: caso queira restaurar estoque ao deletar a venda,
        descomente a seção correspondente.
        """
        session = db.session
        try:
            venda = VendaModel.query.filter_by(id=sale_id, seller_id=seller_id).first()
            if not venda:
                return 0

            # -- Se quiser restaurar estoque ao deletar a venda, habilite abaixo:
            # produto = ProductModel.query.filter_by(id=venda.produto_id).first()
            # if produto:
            #     produto.quantidade = (produto.quantidade or 0) + venda.quantidade
            #     session.add(produto)

            session.delete(venda)
            session.commit()
            return 1
        except Exception as e:
            session.rollback()
            raise Exception(f"Erro interno ao excluir venda: {e}")

    def _map_model_to_domain(self, model: VendaModel) -> VendaDomain:
        """
        Mapeia VendaModel para VendaDomain.
        Ajuste os campos retornados conforme o seu VendaDomain.
        """
        return VendaDomain(
            id=model.id,
            produto_id=model.produto_id,
            quantidade=model.quantidade,
            preco_vendido=model.preco_vendido,
            seller_id=model.seller_id,
            created_at=model.created_at
        )

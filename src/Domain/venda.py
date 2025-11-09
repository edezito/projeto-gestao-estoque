from typing import Optional, Union, Dict, Any
from datetime import datetime

class VendaDomain:
    """
    Representa o domínio de uma venda dentro da aplicação.
    """

    def __init__(
        self,
        id: Optional[int],
        produto_id: int,
        seller_id: int,
        quantidade: int,
        preco_vendido: Union[float, int],
        created_at: Optional[datetime] = None,
        # ✅ PASSO 1.1: Adicione um parâmetro para receber os detalhes do produto
        produto_details: Optional[Dict[str, Any]] = None 
    ):
        self.id = id
        self.produto_id = produto_id
        self.seller_id = seller_id
        self.quantidade = int(quantidade)
        self.preco_vendido = float(preco_vendido)
        self.created_at = created_at or datetime.utcnow()
        # ✅ PASSO 1.2: Armazene os detalhes
        self.produto_details = produto_details

    def to_dict(self) -> dict:
        """Retorna uma representação do domínio em formato de dicionário."""
        return {
            "id": self.id,
            "produto_id": self.produto_id,
            "seller_id": self.seller_id,
            "quantidade": self.quantidade,
            "preco_vendido": self.preco_vendido,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # ✅ PASSO 1.3: Adicione os detalhes do produto ao JSON final
            "produto": self.produto_details 
        }

    def __repr__(self):
        """Representação útil para depuração."""
        return (
            f"<VendaDomain produto_id={self.produto_id}, "
            f"quantidade={self.quantidade}, produto={self.produto_details}>"
        )
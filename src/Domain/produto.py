from typing import Optional, Union


class ProductDomain:
    """
    Representa o domínio de um produto dentro da aplicação.
    É a camada de abstração entre o banco de dados e as regras de negócio.
    """

    def __init__(
        self,
        id: Optional[int],
        user_id: int,
        nome: str,
        preco: Union[float, int],
        quantidade: int,
        status: str = "Ativo",
        imagem: Optional[str] = None
    ):
        self.id = id
        self.user_id = user_id
        self.nome = nome.strip() if isinstance(nome, str) else nome
        self.preco = float(preco)
        self.quantidade = int(quantidade)
        self.status = status.capitalize() if isinstance(status, str) else status
        self.imagem = imagem

    def to_dict(self) -> dict:
        """Retorna uma representação do domínio em formato de dicionário."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nome": self.nome,
            "preco": self.preco,
            "quantidade": self.quantidade,
            "status": self.status,
            "imagem": self.imagem
        }

    def __repr__(self):
        """Representação útil para depuração."""
        return f"<ProductDomain nome={self.nome}, preco={self.preco}, quantidade={self.quantidade}>"

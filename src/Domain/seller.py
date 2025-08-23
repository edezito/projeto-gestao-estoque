#ENTIDADE DE DOMÍNIO

from dataclasses import dataclass
from typing import Optional

@dataclass
class Seller:
    id: Optional[int]
    nome: str
    cnpj: str
    email: str
    celular: str
    senha: str
    status: str = "Inativo"
    codigo_ativacao: Optional[str] = None

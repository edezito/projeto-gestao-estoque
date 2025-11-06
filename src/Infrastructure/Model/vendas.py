from src.Config import db
from datetime import datetime


class VendaModel(db.Model):
    __tablename__ = 'vendas'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    quantidade = db.Column(db.Integer, nullable=False)
    preco_vendido = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    produto = db.relationship('ProductModel', backref=db.backref('vendas', lazy=True))
    seller = db.relationship('UserModel', backref=db.backref('vendas', lazy=True))

    def to_dict(self):
        """Retorna uma representação do modelo em formato de dicionário."""
        return {
            "id": self.id,
            "produto_id": self.produto_id,
            "seller_id": self.seller_id,
            "quantidade": self.quantidade,
            "preco_vendido": self.preco_vendido,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

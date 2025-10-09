from src.Config import db

class ProductModel(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="Ativo")
    imagem = db.Column(db.String(255), nullable=True)

    # Chave estrangeira que aponta para o 'id' da tabela 'users'.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel', backref=db.backref('products', lazy=True))

    def to_dict(self):
        """Retorna uma representação do modelo em formato de dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "preco": self.preco,
            "quantidade": self.quantidade,
            "status": self.status,
            "imagem": self.imagem,
            "user_id": self.user_id 
        }
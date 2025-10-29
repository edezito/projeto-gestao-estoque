import os
from flask import Flask
from src.Config import db, init_db
from src.Application.Controllers.user_controllers import UserController
from src.Application.Controllers.produto_controller import ProductController

def create_app():
    app = Flask(__name__)

    database_url = os.environ.get('DATABASE_URL')

    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ.get('SENHA_JWT')

    # Inicializa o banco de dados
    db.init_app(app)
    init_db(app)

    # Instancia o controlador
    user_controller = UserController()
    product_controller = ProductController()

    # Registra o blueprint do controlador
    app.register_blueprint(user_controller.blueprint, url_prefix='/api/users')
    app.register_blueprint(product_controller.blueprint, url_prefix='/api/products')

    # Rota raiz
    @app.route('/')
    def home():
        return {"message": "API funcionando"}

    return app

# Variável global para Gunicorn
app = create_app()
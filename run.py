import os
from flask import Flask, request, jsonify
from flask_cors import CORS 
from src.Config import db, init_db
from src.Application.Controllers.user_controllers import UserController
from src.Application.Controllers.produto_controller import ProductController
from src.Application.Controllers.venda_controller import VendaController 

def create_app():
    app = Flask(__name__)

    # Configuração CORS MAIS PERMISSIVA para debugging
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Pega a URL do banco de dados do ambiente
    database_url = os.environ.get('DATABASE_URL')

    # Correção para o formato de conexão do SQLAlchemy no Python 3+
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SENHA_JWT')

    # Inicializa o banco de dados
    db.init_app(app)
    init_db(app)

    # Handler global para OPTIONS (preflight)
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({"status": "preflight"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
            response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
            return response

    # Adiciona headers CORS em todas as respostas
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Instancia o controlador
    user_controller = UserController()
    product_controller = ProductController()
    venda_controller = VendaController()

    # Registra o blueprint do controlador
    app.register_blueprint(user_controller.blueprint, url_prefix='/api/users')
    app.register_blueprint(product_controller.blueprint, url_prefix='/api/products')
    app.register_blueprint(venda_controller.blueprint, url_prefix='/api/vendas') 

    # Rota raiz
    @app.route('/')
    def home():
        return {"message": "API funcionando"}

    return app

# Variável global para Gunicorn
app = create_app()
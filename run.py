import os
from flask import Flask
from flask_cors import CORS 
from src.Config import db, init_db
from src.Application.Controllers.user_controllers import UserController
from src.Application.Controllers.produto_controller import ProductController
from src.Application.Controllers.venda_controller import VendaController 

def create_app():
    app = Flask(__name__)

    frontend_urls_env = os.environ.get('FRONTEND_URL') 
    
    # 1. Se a variável de ambiente não estiver definida ou for '*': permite TUDO.
    if not frontend_urls_env or frontend_urls_env == '*':
        print("AVISO: CORS está configurado para permitir TODAS as origens ('*').")
        CORS(app)
    else:
        # 2. Divide as URLs da variável de ambiente em uma lista
        allowed_origins = [url.strip() for url in frontend_urls_env.split(',')]
        
        print(f"CORS configurado para permitir: {', '.join(allowed_origins)}")
        
        # Configura o CORS de forma restrita usando a lista de origens.
        CORS(app, resources={
            r"/api/*": {"origins": allowed_origins}
        }, supports_credentials=True)

    # Pega a URL do banco de dados do ambiente
    database_url = os.environ.get('DATABASE_URL')

    # Correção para o formato de conexão do SQLAlchemy no Python 3+
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configura a chave secreta
    app.config['SECRET_KEY'] = os.environ.get('SENHA_JWT')

    # Inicializa o banco de dados
    db.init_app(app)
    init_db(app)

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
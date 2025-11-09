import os
from flask import Flask, request, jsonify
from flask_cors import CORS 
from src.Config import db, init_db
from src.Application.Controllers.user_controllers import UserController
from src.Application.Controllers.produto_controller import ProductController
from src.Application.Controllers.venda_controller import VendaController 

def create_app():
    app = Flask(__name__)

    # ✅ CONFIGURAÇÃO CORS CORRIGIDA
    CORS(app, 
         resources={
             r"/*": {
                 "origins": ["https://mini-mercado-hub.vercel.app", "http://localhost:3000", "http://localhost:5173"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
                 "supports_credentials": True
             }
         })

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
    
    # ✅ MOVER init_db para dentro do contexto da aplicação
    with app.app_context():
        init_db(app)
    
    # Instancia o controlador
    user_controller = UserController()
    product_controller = ProductController()
    venda_controller = VendaController()

    # Registra o blueprint do controlador
    app.register_blueprint(user_controller.blueprint, url_prefix='/api/users')
    app.register_blueprint(product_controller.blueprint, url_prefix='/api/products')
    app.register_blueprint(venda_controller.blueprint, url_prefix='/api/sales')

    # Rota raiz
    @app.route('/')
    def home():
        return {"message": "API funcionando"}

    # ✅ ADICIONE esta rota para health check
    @app.route('/health')
    def health():
        return {"status": "healthy"}, 200

    return app

# ✅ CORREÇÃO: Apenas crie a app quando executado diretamente
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    # ✅ Para Gunicorn, apenas exporte a função create_app
    app = create_app()
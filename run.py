import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS 
from src.Config import db, init_db
from src.Application.Controllers.user_controllers import UserController
from src.Application.Controllers.produto_controller import ProductController
from src.Application.Controllers.venda_controller import VendaController 

def create_app():
    app = Flask(__name__)

    # ✅ CONFIGURAÇÃO CORS ATUALIZADA PARA VERCEL
    CORS(app, 
         resources={
             r"/*": {
                 "origins": [
                     "https://mini-mercado-hub.vercel.app",
                     "http://localhost:3000", 
                     "http://localhost:5173",
                     "https://estoque-web-3513.onrender.com"  # Adicione o próprio Render
                 ],
                 "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
                 "supports_credentials": True,
                 "expose_headers": ["Content-Type", "Authorization"]
             }
         })

    # Pega a URL do banco de dados do ambiente
    database_url = os.environ.get('DATABASE_URL')

    # Correção para o formato de conexão do SQLAlchemy
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SENHA_JWT')

    # Inicializa o banco de dados
    db.init_app(app)
    
    # Adicionar um delay para garantir que o banco esteja pronto
    time.sleep(2)
    
    # ✅ MOVER init_db para dentro do contexto da aplicação
    with app.app_context():
        try:
            init_db(app)
            print("✅ Banco de dados inicializado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar banco: {str(e)}")
            # Não falha a app, apenas loga o erro
    
    # Instancia os controladores
    user_controller = UserController()
    product_controller = ProductController()
    venda_controller = VendaController()

    # Registra os blueprints
    app.register_blueprint(user_controller.blueprint, url_prefix='/api/users')
    app.register_blueprint(product_controller.blueprint, url_prefix='/api/products')
    app.register_blueprint(venda_controller.blueprint, url_prefix='/api/sales')

    # Rota raiz
    @app.route('/')
    def home():
        return {"message": "API funcionando", "status": "online"}

    # ✅ HEALTH CHECK - CORRIGIDO PARA /health
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "estoque-api"}, 200

    # ✅ ADICIONE ESTA ROTA PARA TESTE RÁPIDO
    @app.route('/api/test')
    def test():
        return {"message": "API está funcionando!", "timestamp": time.time()}

    return app

# ✅ CORREÇÃO: Apenas crie a app quando executado diretamente
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    app = create_app()
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

    # ✅ CONFIGURAÇÃO CORS - ACEITA TODAS AS ORIGENS
    CORS(app, 
         resources={
             r"/*": {
                 "origins": "*",  # Temporariamente aceita tudo
                 "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "Accept"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })

    # ✅ CONFIGURAÇÃO DO BANCO DE DADOS
    # Use a URL fornecida pelo Render
    database_url = "postgresql://estoque_user:K1vM9MuyLqHSVQPqT6AWGJw97julFJmc@dpg-d4mun4ogjchc73bk89h0-a/estoque_db_oefo"
    
    # Ou pegue do ambiente (se configurado no Render)
    # database_url = os.environ.get('DATABASE_URL', database_url)
    
    print(f"🔗 Conectando ao banco: postgresql://estoque_user:******@dpg-d4mun4ogjchc73bk89h0-a/estoque_db_oefo")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SENHA_JWT', 'senha123')

    # Inicializa o banco de dados
    db.init_app(app)
    
    # ✅ INICIALIZAÇÃO DO BANCO
    with app.app_context():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🔄 Tentativa {attempt + 1}/{max_retries} de conectar ao banco...")
                
                # Testa a conexão
                db.session.execute('SELECT version()')
                print("✅ Conexão com PostgreSQL estabelecida!")
                
                # Cria as tabelas
                print("🔄 Criando tabelas...")
                db.create_all()
                
                # Inicializa dados se necessário
                try:
                    init_db(app)
                    print("✅ Dados iniciais configurados!")
                except Exception as init_error:
                    print(f"⚠️ Erro no init_db: {init_error}")
                    print("⚠️ Continuando sem dados iniciais...")
                
                break  # Sai do loop se conseguir
                
            except Exception as e:
                print(f"❌ Erro na tentativa {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"⏳ Aguardando 5 segundos antes de tentar novamente...")
                    time.sleep(5)
                else:
                    print("❌ Falha após todas as tentativas. Continuando sem banco...")
    
    # ✅ HANDLERS CORS MANUAIS
    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,PATCH,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            response = jsonify({'status': 'preflight ok'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,PATCH,OPTIONS')
            return response
    
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
        return {"message": "API funcionando", "status": "online", "database": "postgresql"}

    # ✅ HEALTH CHECK melhorado
    @app.route('/health')
    def health():
        try:
            db.session.execute('SELECT 1')
            return {
                "status": "healthy", 
                "service": "estoque-api",
                "database": "connected",
                "timestamp": time.time()
            }, 200
        except Exception as e:
            return {
                "status": "degraded", 
                "service": "estoque-api",
                "database": "disconnected",
                "error": str(e)[:100],
                "timestamp": time.time()
            }, 200

    # ✅ ROTA DE TESTE
    @app.route('/api/test')
    def test():
        return {
            "message": "API funcionando",
            "database": "PostgreSQL",
            "cors": "enabled",
            "timestamp": time.time()
        }

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    app = create_app()
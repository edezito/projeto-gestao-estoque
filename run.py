from flask import Flask
from src.Config import db, init_db
from src.Application.Controllers.user_controllers import UserController

def create_app():
    app = Flask(__name__)

    # Configurações básicas do Flask
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://user:user@db:3306/estoque_mercado"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "uma_chave_secreta"

    # Inicializa o banco de dados
    db.init_app(app)
    init_db(app)

    # Instancia o controlador
    user_controller = UserController()

    # Registra o blueprint do controlador
    app.register_blueprint(user_controller.blueprint, url_prefix='/api/users')

    # Rota raiz
    @app.route('/')
    def home():
        return {"message": "API funcionando"}

    return app

# Variável global para Gunicorn
app = create_app()
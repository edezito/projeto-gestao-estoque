from src.Application.Controllers.user_controllers import UserController

# Instancia o controlador (fora da função para ser reutilizável)
user_controller = UserController()

def register_routes(app):
    """Registra todas as rotas e blueprints"""
    
    # Registra o blueprint de usuários (usa a instância já criada)
    app.register_blueprint(user_controller.blueprint, url_prefix='/api/users')
    
    # Rota raiz
    @app.route('/')
    def home():
        return {"message": "API funcionando"}
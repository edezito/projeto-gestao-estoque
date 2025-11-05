import pytest
import json

@pytest.fixture
def client():
    from run import create_app
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- TESTES BÁSICOS (validações e erros) - ESTES FUNCIONAM ---

def test_register_user_missing_fields(client):
    """Testa registro com campos faltando"""
    response = client.post('/api/users/register', 
                         json={"nome": "Mercado Teste"})
    
    assert response.status_code == 400
    data = response.get_json()
    assert "faltando" in data.get('erro', '')

def test_activate_user_missing_data(client):
    """Testa ativação com dados faltando"""
    response = client.post('/api/users/activate', 
                         json={})  # CNPJ e código faltando
    
    assert response.status_code == 400
    data = response.get_json()
    assert "obrigatórios" in data.get('erro', '')

def test_login_missing_credentials(client):
    """Testa login com credenciais faltando"""
    response = client.post('/api/users/login', 
                         json={})  # Login e senha faltando
    
    assert response.status_code == 400
    data = response.get_json()
    assert "obrigatórios" in data.get('erro', '')

def test_protected_route_no_token(client):
    """Testa acesso a rota protegida sem token"""
    response = client.get('/api/users/1')
    assert response.status_code == 401
    data = response.get_json()
    assert "Token" in data.get('message', '')

def test_invalid_json(client):
    """Testa envio de JSON inválido"""
    response = client.post('/api/users/register', 
                         data="invalid json", 
                         content_type='application/json')
    
    assert response.status_code == 400

def test_user_routes_exist(client):
    """Testa se as rotas de usuário existem e respondem"""
    routes = [
        ('/api/users/register', 'POST'),
        ('/api/users/activate', 'POST'), 
        ('/api/users/login', 'POST'),
        ('/api/users/1', 'GET'),
    ]
    
    for route, method in routes:
        if method == 'GET':
            response = client.get(route)
        elif method == 'POST':
            response = client.post(route, json={})
        
        # Não deve ser 404 (rota não encontrada) ou 405 (método não permitido)
        assert response.status_code not in [404, 405]
import jwt
import os
from functools import wraps
from flask import request, jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'authorization' in request.headers:
            try:
                token = request.headers['authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Header de autorização mal formatado.'}), 401

        if not token:
            return jsonify({'message': 'Token não encontrado!'}), 401
        
        try:
            secret_key = os.getenv('JWT_SECRET')
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            # Payload esperando 'id' e 'nome'
            current_user = {'id': data['id'], 'nome': data['nome']}
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirou!'}), 403
        except (jwt.InvalidTokenError, KeyError):
            return jsonify({'message': 'Token inválido ou payload incorreto.'}), 403
        
        # Passa o usuário decodificado para a rota
        return f(current_user, *args, **kwargs)
    return decorated
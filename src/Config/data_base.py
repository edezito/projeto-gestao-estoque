from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Inicializa o banco de dados e cria tabelas se não existirem."""
    with app.app_context():
        try:
            # Tenta criar todas as tabelas
            db.create_all()
            print("✅ Banco de dados inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            # Em caso de erro, tenta uma abordagem mais simples
            try:
                # Verifica se a tabela users existe de forma alternativa
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                if 'users' not in inspector.get_table_names():
                    db.create_all()
                    print("✅ Tabelas criadas com sucesso")
                else:
                    print("✅ Tabelas já existem")
            except Exception as e2:
                print(f"❌ Erro secundário ao verificar banco de dados: {e2}")
class UserDomain:
    def __init__(self, id, nome, cnpj, email, celular, senha, status="Inativo", codigo_ativacao=None):
        self.id = id
        self.nome = nome
        self.cnpj = cnpj
        self.email = email
        self.celular = celular
        self.senha = senha
        self.status = status
        self.codigo_ativacao = codigo_ativacao

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cnpj": self.cnpj,
            "email": self.email,
            "celular": self.celular,
            "status": self.status
        }
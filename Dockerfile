FROM python:3.10-slim

WORKDIR /src

# Instalar dependências do sistema necessárias para MySQL e build
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Atualiza pip e instala dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação
COPY . .

EXPOSE 5000

# Variáveis de ambiente padrão
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Rodar Gunicorn apontando para a variável global 'app' em run.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]

FROM python:3.10-slim

WORKDIR /src

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cache
COPY requirements.txt .

# Atualiza pip e instala dependências
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p /var/log/app

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

# Health check (para Docker)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; r = requests.get('http://localhost:5000/health', timeout=5); exit(0) if r.status_code == 200 else exit(1)" || exit 1

# Rodar Gunicorn com configurações otimizadas
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--preload", \
     "run:app"]
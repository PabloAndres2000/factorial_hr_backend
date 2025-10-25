FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Actualizar sistema e instalar herramientas necesarias
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

# Copiar el código
COPY . /app/

# Scripts
COPY start_app.sh /usr/local/bin/start_app
COPY .docker/dev /usr/local/bin/dev
RUN chmod +x /usr/local/bin/start_app /usr/local/bin/dev

# Crear logs
RUN mkdir -p /app/logs && touch /app/logs/tasks.log

# Exponer puertos
EXPOSE 8000 8081 8082

# Comando por defecto
CMD ["bash", "start_app"]

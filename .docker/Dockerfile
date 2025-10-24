FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar todo el código al contenedor
COPY . /app/

# Preparar scripts en una sola capa
COPY start_app.sh /usr/local/bin/start_app
COPY .docker/dev /usr/local/bin/dev
RUN chmod +x /usr/local/bin/start_app /usr/local/bin/dev

# Preparar directorios y archivos en una sola capa
RUN mkdir -p /app/logs && touch /app/logs/tasks.log

# Exponer los puertos en una sola línea
EXPOSE 8000 8081 8082

# Configurar el comando por defecto
CMD ["bash", "start_app"]

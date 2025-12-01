# Imagen base de Python
FROM python:3.11-slim

# Establece directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . /app

# Instala dependencias
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expone el puerto que Railway usa
ENV PORT=8000

# Comando para ejecutar tu app con Gunicorn
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT

# Imagen base de Python, recomendamos una versión slim para contenedores más pequeños
FROM python:3.11-slim

# Establece directorio de trabajo
WORKDIR /app

# 1. Copia solo el archivo de dependencias primero para aprovechar el cache de Docker
# Si requirements.txt no cambia, esta capa no se reconstruye.
COPY requirements.txt /app/

# 2. Instala dependencias (gunicorn debe estar aquí)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 3. Copia el resto de los archivos del proyecto (incluyendo tu código)
# Este paso se ejecuta cada vez que el código cambia.
COPY . /app

# 4. Configuración del puerto
# El puerto 8000 es el estándar de Gunicorn, pero es buena práctica usar la variable.
ENV PORT=8000

# 5. Comando para ejecutar tu app con Gunicorn
# Asegúrate de que 'config.wsgi:application' sea el path correcto a tu aplicación WSGI.
# El error de "gunicorn: not found" se corregirá una vez que se instale en el paso 2.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
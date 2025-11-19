# ---------------------------------------------------------------
#    Dockerfile (v 2.1)
# ---------------------------------------------------------------

# 1. Imagen base
FROM python:3.11-slim

# 2. Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecer el directorio de trabajo en /code (un nivel ARRIBA de tu app)
WORKDIR /code

# 4. Copiar requirements e instalar
# (Copia requirements.txt a /code/requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar la aplicación
# (Copia tu carpeta local 'app' a '/code/app')
COPY ./app /code/app

# 6. Exponer el puerto
EXPOSE 8000

# 7. Healthcheck (Esto ya lo tenías y está bien)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 8. Comando de inicio (LA CORRECCIÓN CLAVE)
# Le decimos a Uvicorn que ejecute el MÓDULO 'app.main', variable 'app'
# Python ahora buscará en /code/app/main.py, y los imports 'app.' funcionarán
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
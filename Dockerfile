# ---------------------------------------------------------------
#    Dockerfile (v 2.0)
# ---------------------------------------------------------------

# 1. Imagen base
FROM python:3.11-slim

# 2. Directorio de trabajo
WORKDIR /app

# 3. Instalar dependencias del sistema (ej. gcc, necesario para algunas librerías)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiar requirements e instalar (para aprovechar el caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar la aplicación (Solo la carpeta 'app')
COPY ./app /app

# 6. Exponer el puerto
EXPOSE 8000

# 7. Healthcheck (basado en el endpoint de tu main.py)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 8. Comando de inicio (Usa /app/main.py, ya que WORKDIR es /app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
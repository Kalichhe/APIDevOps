FROM python:3.14-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Exponer el puerto
EXPOSE 8000

# Comando para correr la app
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
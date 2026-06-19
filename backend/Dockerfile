FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para pdfplumber y psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Directorio de uploads
RUN mkdir -p /var/app/uploads

# Ejecutar como usuario no-root
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app /var/app/uploads
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.10-slim

# netcat (nc) yükle - wait script için gerekli
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Wait script'i çalıştırılabilir yap
RUN chmod +x wait-for-postgres.sh

# PostgreSQL hazır olana kadar bekle, sonra ETL'i çalıştır
CMD ["./wait-for-postgres.sh", "postgres", "5432", "python", "etl_pipeline.py"]

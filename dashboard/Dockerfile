FROM python:3.10-slim

# Sistem paketleri (psycopg2 için gerekli)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements dosyasını kopyala
COPY requirements.txt .

# Gerekli tüm Python paketlerini yükle
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyası
COPY app.py .

# Streamlit çalıştır
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
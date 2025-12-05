# 📰 HuffPost News – ETL + Dashboard Projesi

Bu proje, **Mid-Level Data Engineer** portföy projesi seviyesinde, gerçek bir haber veri setini profesyonel bir ETL Pipeline ile işleyip PostgreSQL'e yükleyen ve Streamlit ile interaktif bir dashboard sunan kapsamlı bir veri mühendisliği projesidir.

## 🎯 Proje Amacı

- ✅ Kaggle'dan alınan gerçek bir haber veri setini işlemek
- ✅ Profesyonel bir ETL Pipeline ile veriyi dönüştürmek
- ✅ Veriyi PostgreSQL (Data Warehouse) ortamına yüklemek
- ✅ Streamlit ile interaktif veri analizi dashboardu oluşturmak
- ✅ NLP (Sentiment Analysis + Word Cloud) gibi ek analizler eklemek

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │   ETL        │──────▶│  PostgreSQL  │◀─────│Dashboard │ │
│  │  Pipeline    │      │  (Data       │      │(Streamlit)│ │
│  │              │      │  Warehouse)  │      │           │ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│         │                      │                    │      │
│         └──────────────────────┴────────────────────┘      │
│                    Docker Network                           │
└─────────────────────────────────────────────────────────────┘
```

### Servisler

1. **ETL Service** (`news_etl`)
   - Kaggle veri setini okur
   - Veriyi dönüştürür (tarih temizleme, sentiment analysis)
   - PostgreSQL'e yükler
   - Wait-for-postgres script ile PostgreSQL hazır olana kadar bekler

2. **PostgreSQL** (`news_postgres`)
   - Data Warehouse görevi görür
   - 3 tablo içerir:
     - `raw_news`: Ham haber verileri
     - `category_stats`: Kategori bazlı istatistikler
     - `sentiment_news`: Sentiment analizi sonuçları

3. **Dashboard** (`news_dashboard`)
   - Streamlit ile interaktif dashboard
   - PostgreSQL'den veri okur
   - Grafikler ve filtreler sunar

## 📊 Veri Seti

- **Kaynak**: Kaggle - News Category Dataset v3
- **Kayıt Sayısı**: 209,527 haber
- **Kategoriler**: 42 farklı kategori
- **Özellikler**: Headline, Category, Publish Date

## 🛠️ Teknolojiler

- **ETL**: Python, Pandas, SQLAlchemy
- **NLP**: NLTK, VADER Sentiment Analysis
- **Database**: PostgreSQL 15
- **Dashboard**: Streamlit
- **Containerization**: Docker, Docker Compose
- **Visualization**: Matplotlib, WordCloud

## 📦 Kurulum

### Gereksinimler

- Docker
- Docker Compose
- Kaggle veri seti (`News_Category_Dataset_v3.json`)

### Adımlar

1. **Projeyi klonlayın veya indirin**

```bash
git clone <repo-url>
cd etl_pipeline
```

2. **Veri dosyasını yerleştirin**

Kaggle'dan indirdiğiniz `News_Category_Dataset_v3.json` dosyasını `data/` klasörüne koyun:

```bash
data/News_Category_Dataset_v3.json
```

3. **Docker container'ları başlatın**

```bash
docker-compose up -d
```

Bu komut şunları yapar:
- PostgreSQL container'ını başlatır
- ETL pipeline'ı çalıştırır (PostgreSQL hazır olana kadar bekler)
- Dashboard'ı başlatır

4. **ETL loglarını kontrol edin**

```bash
docker logs news_etl
```

5. **Dashboard'a erişin**

Tarayıcınızda şu adrese gidin:
```
http://localhost:8501
```

## 🔍 Veritabanı Kontrolü

PostgreSQL'e bağlanıp tabloları kontrol edebilirsiniz:

```bash
docker exec -it news_postgres psql -U news_user -d news_db
```

PostgreSQL içinde:

```sql
-- Tabloları listele
\dt

-- Kayıt sayılarını kontrol et
SELECT COUNT(*) FROM raw_news;
SELECT COUNT(*) FROM category_stats;
SELECT COUNT(*) FROM sentiment_news;

-- Kategori istatistiklerini görüntüle
SELECT * FROM category_stats ORDER BY count DESC LIMIT 10;
```

## 📈 Dashboard Özellikleri

Dashboard şu grafikleri ve özellikleri sunar:

1. **Kategori Bazlı Haber Dağılımı**
   - Horizontal bar chart
   - Her kategorideki haber sayısı

2. **Zaman Serisi Trend Grafiği**
   - Günlük / Aylık / Yıllık çözünürlük seçimi
   - Kategori bazlı multi-line trend

3. **Top 10 En Yoğun Gün**
   - En çok haber üretilen günler

4. **Word Cloud**
   - Headline verilerinden kelime bulutu
   - Kategori filtresine göre dinamik

5. **Sentiment Dağılım Grafiği**
   - Positive / Neutral / Negative sınıflandırması
   - Kategori bazlı sentiment analizi

### Filtreler

- **Kategori Seçimi**: Birden fazla kategori seçebilirsiniz
- **Zaman Çözünürlüğü**: Günlük, Aylık, Yıllık

## 🔄 ETL Pipeline Detayları

### Extract (Veri Çekme)
- Kaggle JSON dosyasını okur
- 200,000+ satırlık veriyi yükler

### Transform (Veri İşleme)
- Tarih kolonlarını temizler ve `publish_date` üretir
- Gereksiz alanları çıkarır
- Kategorilere göre haber sayılarını hesaplar
- **NLP İşlemleri**:
  - VADER Sentiment Analysis ile sentiment skoru hesaplar
  - Positive / Neutral / Negative sınıflandırması yapar
  - Word Cloud için metin temizliği

### Load (Veri Yükleme)
- PostgreSQL'e 3 tablo olarak yükler:
  - `raw_news`: Ham haber verileri
  - `category_stats`: Kategori istatistikleri
  - `sentiment_news`: Sentiment analizi sonuçları

## 🐛 Sorun Giderme

### ETL Container Çalışmıyor

```bash
# Logları kontrol edin
docker logs news_etl

# Container'ı yeniden başlatın
docker-compose restart etl
```

### PostgreSQL Bağlantı Hatası

```bash
# PostgreSQL'in çalıştığını kontrol edin
docker ps | grep postgres

# PostgreSQL loglarını kontrol edin
docker logs news_postgres
```

### Dashboard Veri Görmüyor

1. ETL'in başarıyla tamamlandığını kontrol edin:
```bash
docker logs news_etl | grep "tamamlandı"
```

2. PostgreSQL'de tabloların olduğunu kontrol edin:
```bash
docker exec -it news_postgres psql -U news_user -d news_db -c "\dt"
```

3. Dashboard'ı yeniden başlatın:
```bash
docker-compose restart dashboard
```

## 📁 Proje Yapısı

```
etl_pipeline/
├── docker-compose.yaml       # Docker Compose konfigürasyonu
├── README.md                 # Bu dosya
│
├── etl/                      # ETL Pipeline servisi
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── etl_pipeline.py      # Ana ETL kodu
│   └── wait-for-postgres.sh # PostgreSQL bekleme scripti
│
├── dashboard/                # Streamlit Dashboard servisi
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py               # Dashboard uygulaması
│
├── data/                     # Veri dosyaları
│   ├── News_Category_Dataset_v3.json
│   └── news_etl.db          # SQLite (eski, artık kullanılmıyor)
│
└── output/                   # Çıktı dosyaları
    └── category_distribution.png
```

## 🚀 Gelişmiş Özellikler (Gelecek Planlar)

Bu proje Senior Data Engineer seviyesine çıkmak için şu özellikler eklenebilir:

- 🔹 **Airflow**: ETL pipeline'ı zamanlamak için
- 🔹 **dbt**: Dönüşüm katmanı eklemek için
- 🔹 **Snowflake / BigQuery**: Cloud data warehouse entegrasyonu
- 🔹 **Kubernetes**: Production deployment için
- 🔹 **REST API**: Haber sorgulama API'si
- 🔹 **Grafana + TimescaleDB**: Real-time dashboard

## 📝 Lisans

Bu proje eğitim amaçlıdır.

## 👤 Yazar

Mid-Level Data Engineer Portföy Projesi

---

**Not**: Bu proje Docker kullanarak geliştirilmiştir. Tüm bağımlılıklar container içinde yönetilir ve sisteminize ek paket yüklemeniz gerekmez.


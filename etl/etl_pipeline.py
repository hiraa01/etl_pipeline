import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# VADER sözlüğünü indir (ilk çalıştırmada lazım)
nltk.download("vader_lexicon")


# ============================================================
#                     EXTRACT
# ============================================================
def extract():
    print("Extracting data...")

    # Kaggle HuffPost dataset JSON
    df = pd.read_json("/app/data/News_Category_Dataset_v3.json", lines=True)

    print(f"Toplam kayıt sayısı: {len(df)}")
    return df


# ============================================================
#                     TRANSFORM
# ============================================================
def transform(df):
    print("Transforming data...")

    # date kolonunu datetime'e çevir
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # publish_date (sadece tarih) üret
    df["publish_date"] = df["date"].dt.date

    # publish_date boş olanları at
    df = df.dropna(subset=["publish_date"])

    # Sadece ihtiyacımız olan kolonlar
    df = df[["headline", "category", "publish_date"]]

    # -------- SENTIMENT ANALYSIS --------
    sia = SentimentIntensityAnalyzer()

    # her headline için compound skor
    df["sentiment"] = df["headline"].apply(
        lambda x: sia.polarity_scores(x)["compound"]
    )

    # skorları label'a çevir
    def label_sentiment(score):
        if score > 0.05:
            return "Positive"
        elif score < -0.05:
            return "Negative"
        else:
            return "Neutral"

    df["sentiment_label"] = df["sentiment"].apply(label_sentiment)

    # -------- CATEGORY COUNTS --------
    category_counts = (
        df.groupby("category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    print("En çok haber içeren 5 kategori:")
    print(category_counts.head())

    return df, category_counts


# ============================================================
#                     LOAD → PostgreSQL
# ============================================================
def load(df, category_counts):
    print("Loading data into PostgreSQL...")

    # Docker içinden erişim: host = postgres, port = 5432
    engine = create_engine(
        "postgresql://news_user:news_pass@postgres:5432/news_db"
    )

    # Ham haberler (dashboard trend + wordcloud buradan okuyacak)
    df.to_sql("raw_news", engine, if_exists="replace", index=False)

    # Sentiment tablosu
    df_sent = df[["headline", "category", "publish_date", "sentiment", "sentiment_label"]].copy()
    df_sent.to_sql("sentiment_news", engine, if_exists="replace", index=False)

    # Kategori istatistikleri
    category_counts.to_sql("category_stats", engine, if_exists="replace", index=False)

    print("Veriler PostgreSQL veritabanına başarıyla yüklendi!")


# ============================================================
#                     VISUALIZE
# ============================================================
def visualize(category_counts):
    print("Creating bar chart...")

    plt.figure(figsize=(12, 8))
    plt.barh(category_counts["category"], category_counts["count"], color="skyblue")
    plt.xlabel("News Count")
    plt.ylabel("Category")
    plt.title("News Category Distribution")
    plt.tight_layout()
    plt.savefig("/app/output/category_distribution.png")
    plt.close()

    print("Grafik kaydedildi: output/category_distribution.png")


# ============================================================
#                     MAIN
# ============================================================
def main():
    print("ETL Pipeline başlatılıyor...")

    df = extract()
    df, category_counts = transform(df)
    load(df, category_counts)
    visualize(category_counts)

    print("ETL Pipeline tamamlandı!")


if __name__ == "__main__":
    main()
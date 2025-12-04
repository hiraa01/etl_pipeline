import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

def extract():
    print("Extracting data...")

    df = pd.read_json("/app/data/News_Category_Dataset_v3.json", lines=True)

    print(f"Toplam kayıt sayısı: {len(df)}")
    return df


def transform(df):
    print("Transforming data...")

    # Date kolonunu datetime yap
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # publish_date üret
    df["publish_date"] = df["date"].dt.date

    # publish_date olmayanları at
    df = df.dropna(subset=["publish_date"])

    # Sadece gerekli kolonları bırak
    df = df[["headline", "category", "publish_date"]]

    # Kategori istatistikleri
    category_counts = (
        df.groupby("category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    return df, category_counts


def load(df, category_counts):
    print("Loading data into SQLite database...")
    conn = sqlite3.connect("/app/data/news_etl.db")

    # Ham veri
    df.to_sql("raw_news", conn, if_exists="replace", index=False)

    # Kategori istatistikleri
    category_counts.to_sql("category_stats", conn, if_exists="replace", index=False)

    conn.close()
    print("Veriler SQLite veritabanına başarıyla yüklendi!")


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

    print("Grafik oluşturuldu: output/category_distribution.png")


def main():
    print("ETL Pipeline başlatılıyor...")

    df = extract()
    df, category_counts = transform(df)  
    load(df, category_counts)
    visualize(category_counts)

    print("ETL Pipeline başarıyla tamamlandı!")


if __name__ == "__main__":
    main()
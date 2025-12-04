import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

def extract():
    print("Extracting data...")

    # Kaggle News Category JSON dosyasını oku
    df = pd.read_json("/app/data/News_Category_Dataset_v3.json", lines=True)

    print(f"Toplam kayıt sayısı: {len(df)}")
    return df


def transform(df):
    print("Transforming data...")

    # Tarih formatını pandas datetime'e çevir
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Gereksiz kolonları çıkar
    df = df[["headline", "category", "date"]]

    # Kategorilere göre haber sayısı
    category_counts = (
        df.groupby("category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    print("En çok haber içeren ilk 5 kategori:")
    print(category_counts.head())

    return category_counts


def load(df_raw, category_counts):
    print("Loading data into SQLite database...")

    conn = sqlite3.connect("/app/data/news_etl.db")

    # RAW NEWS → Trend Analizi için gerekli tablo
    df_raw.to_sql("raw_news", conn, if_exists="replace", index=False)

    # CATEGORY STATS → kategori dağılımı için
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

    # Grafiği kaydet
    plt.savefig("/app/output/category_distribution.png")
    plt.close()

    print("Grafik oluşturuldu: output/category_distribution.png")    


def main():
    print("ETL Pipeline başlatılıyor...")

    df = extract()
    category_counts = transform(df)
    load(df, category_counts)
    visualize(category_counts)


    print("ETL Pipeline başarıyla tamamlandı!")


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# =====================================================================
#                           DATABASE CONNECTION
# =====================================================================
@st.cache_data
def load_data():
    conn = sqlite3.connect("file:/app/data/news_etl.db?mode=ro", uri=True)

    # Category table
    category_df = pd.read_sql_query("SELECT * FROM category_stats", conn)

    # Trend table (category + publish_date)
    trend_df = pd.read_sql_query("""
        SELECT category, publish_date, COUNT(*) as count
        FROM raw_news
        GROUP BY category, publish_date
        ORDER BY publish_date ASC
    """, conn)

    conn.close()
    return category_df, trend_df


# =====================================================================
#                           PAGE SETTINGS
# =====================================================================
st.set_page_config(page_title="HuffPost News Dashboard", layout="wide")

st.title("HuffPost News Dashboard")
st.write("Veri Kaynağı: Kaggle • ETL: Docker • Dashboard: Streamlit")


# =====================================================================
#                           LOAD DATA
# =====================================================================
category_df, trend_df = load_data()
trend_df["publish_date"] = pd.to_datetime(trend_df["publish_date"], errors="coerce")


# =====================================================================
#                           SIDEBAR FILTERS
# =====================================================================
st.sidebar.header("🔎 Filtreler")

selected_category = st.sidebar.multiselect(
    "Kategori Seç:",
    options=category_df["category"].unique(),
    default=category_df["category"].unique()
)

time_resolution = st.sidebar.selectbox(
    "Zaman Çözünürlüğü:",
    ["Günlük", "Aylık", "Yıllık"]
)

# Filtre uygulanmış veri
filtered_df = category_df[category_df["category"].isin(selected_category)]
trend_filtered = trend_df[trend_df["category"].isin(selected_category)]


# =====================================================================
#                           TWO COLUMN LAYOUT
# =====================================================================
col1, col2 = st.columns(2)

# ---------------------- LEFT CHART ----------------------
with col1:
    st.subheader("Kategoriye Göre Haber Dağılımı")

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.barh(filtered_df["category"], filtered_df["count"], color="skyblue")
    ax1.set_xlabel("Haber Sayısı")
    ax1.set_ylabel("Kategori")
    plt.tight_layout()
    st.pyplot(fig1)

# ---------------------- RIGHT CHART ----------------------
with col2:
    st.subheader("Kategori Bazlı Zaman Serisi Trend Grafiği")

    trend_resampled = trend_filtered.copy().set_index("publish_date")

    if time_resolution == "Aylık":
        trend_resampled = (
            trend_resampled
            .groupby("category")
            .resample("M")["count"]
            .sum()
            .reset_index()
        )
    elif time_resolution == "Yıllık":
        trend_resampled = (
            trend_resampled
            .groupby("category")
            .resample("Y")["count"]
            .sum()
            .reset_index()
        )
    else:
        trend_resampled = trend_filtered.copy()

    fig2, ax2 = plt.subplots(figsize=(6, 4))

    for cat in selected_category:
        cat_data = trend_resampled[trend_resampled["category"] == cat]
        ax2.plot(cat_data["publish_date"], cat_data["count"], label=cat)

    ax2.set_title(f"Zaman İçinde Haber Sayısı ({time_resolution})")
    ax2.set_xlabel("Tarih")
    ax2.set_ylabel("Haber Adedi")
    ax2.grid(True)
    ax2.legend(fontsize=7)

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)


# =====================================================================
#                           CATEGORY TABLE
# =====================================================================
st.subheader("📄 Kategori İstatistikleri Tablosu")
st.dataframe(filtered_df, use_container_width=True)


# =====================================================================
#           CATEGORY-BASED SENTIMENT BAR CHART  (NEW)
# =====================================================================
st.subheader("Kategori Bazlı Duygu Dağılımı (Sentiment Analysis)")

# Sentiment tablosunu oku
conn = sqlite3.connect("file:/app/data/news_etl.db?mode=ro", uri=True)
sent_df = pd.read_sql_query("""
    SELECT category, sentiment_label
    FROM sentiment_news
""", conn)
conn.close()

# Seçili kategoriler için filtre
sent_df = sent_df[sent_df["category"].isin(selected_category)]

if not sent_df.empty:
    sent_counts = (
        sent_df.groupby(["category", "sentiment_label"])
        .size()
        .reset_index(name="count")
    )

    fig_s, ax_s = plt.subplots(figsize=(10, 5))

    sentiment_order = ["Positive", "Neutral", "Negative"]
    colors = {"Positive": "green", "Neutral": "gray", "Negative": "red"}

    for s in sentiment_order:
        subset = sent_counts[sent_counts["sentiment_label"] == s]
        ax_s.bar(subset["category"], subset["count"], label=s, color=colors[s])

    ax_s.set_title("Kategori Bazlı Duygu Dağılımı")
    ax_s.set_xlabel("Kategori")
    ax_s.set_ylabel("Duygu Sayısı")
    plt.xticks(rotation=45)
    ax_s.legend()
    plt.tight_layout()

    st.pyplot(fig_s)
else:
    st.info("Seçilen kategoriler için duygu analizi bulunamadı.")


# =====================================================================
#          TOP 10 BUSIEST DAYS
# =====================================================================
st.subheader("En Çok Haber Üretilen 10 Gün")

if not trend_filtered.empty:
    top_days = (
        trend_filtered
        .groupby("publish_date")["count"]
        .sum()
        .reset_index()
        .sort_values("count", ascending=False)
        .head(10)
    )

    top_days_display = top_days.copy()
    top_days_display["publish_date"] = top_days_display["publish_date"].dt.strftime("%Y-%m-%d")

    fig3, ax3 = plt.subplots(figsize=(8, 4))
    ax3.bar(top_days_display["publish_date"], top_days_display["count"], color="orange")
    ax3.set_title("En Çok Haber Üretilen 10 Gün")
    ax3.set_xlabel("Tarih")
    ax3.set_ylabel("Haber Sayısı")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig3)

    st.dataframe(top_days_display, use_container_width=True)
else:
    st.info("Seçilen kategoriler için veri bulunamadı.")


# =====================================================================
#                       WORD CLOUD
# =====================================================================
st.subheader("Kelime Bulutu (Headline)")

conn = sqlite3.connect("file:/app/data/news_etl.db?mode=ro", uri=True)
df_raw = pd.read_sql_query("SELECT category, headline FROM raw_news", conn)
conn.close()

df_wc = df_raw[df_raw["category"].isin(selected_category)]

if not df_wc.empty:
    text = " ".join(df_wc["headline"].astype(str))

    from wordcloud import WordCloud, STOPWORDS

    wc = WordCloud(
        width=900,
        height=450,
        background_color="white",
        stopwords=set(STOPWORDS)
    ).generate(text)

    fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
    ax_wc.imshow(wc, interpolation="bilinear")
    ax_wc.axis("off")
    st.pyplot(fig_wc)
else:
    st.info("Bu kategoriler için headline bulunamadı.")
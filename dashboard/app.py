import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# --- DATABASE CONNECTION ---
@st.cache_data
def load_data():
    conn = sqlite3.connect("/app/data/news_etl.db")

    # Category counts
    category_df = pd.read_sql_query("SELECT * FROM category_stats", conn)

    # Trend data (publish_date + count)
    trend_df = pd.read_sql_query("""
        SELECT publish_date, COUNT(*) as count
        FROM raw_news
        GROUP BY publish_date
        ORDER BY publish_date ASC
    """, conn)

    conn.close()
    return category_df, trend_df


# --- PAGE CONFIG ---
st.set_page_config(page_title="HuffPost News Dashboard", layout="wide")

st.title("HuffPost News Dashboard")
st.write("Veri Kaynağı: Kaggle • ETL: Docker + Python • Dashboard: Streamlit")

# --- LOAD DATA ---
category_df, trend_df = load_data()

# Convert publish_date properly
trend_df["publish_date"] = pd.to_datetime(trend_df["publish_date"], errors="coerce")

# --- SIDEBAR FILTER ---
st.sidebar.header("Filtreler")
selected_category = st.sidebar.multiselect(
    "Kategori Seç:",
    options=category_df["category"].unique(),
    default=category_df["category"].unique()
)

filtered_df = category_df[category_df["category"].isin(selected_category)]

# --- CATEGORY BAR CHART ---
st.subheader("Kategoriye Göre Haber Dağılımı")

fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.barh(filtered_df["category"], filtered_df["count"], color="skyblue")
ax1.set_xlabel("News Count")
ax1.set_ylabel("Category")
st.pyplot(fig1)

# --- TREND LINE CHART ---
st.subheader("Haber Sayısı Zaman Serisi (Trend)")

fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.plot(trend_df["publish_date"], trend_df["count"], color="cyan")
ax2.set_title("Zaman İçinde Haber Sayısı")
ax2.set_xlabel("Tarih")
ax2.set_ylabel("Haber Adedi")
ax2.grid(True)
st.pyplot(fig2)

# --- RAW CATEGORY TABLE ---
st.subheader("Kategori Verisi Önizleme")
st.dataframe(filtered_df)

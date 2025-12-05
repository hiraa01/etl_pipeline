import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# --- DATABASE CONNECTION ---
@st.cache_data
def load_data():
    conn = sqlite3.connect("file:/app/data/news_etl.db?mode=ro", uri=True)

    # Category counts (bar chart & table)
    category_df = pd.read_sql_query("SELECT * FROM category_stats", conn)

    # Trend chart (date → count)
    trend_df = pd.read_sql_query("""
        SELECT publish_date, COUNT(*) AS count
        FROM raw_news
        GROUP BY publish_date
        ORDER BY publish_date ASC
    """, conn)

    conn.close()
    return category_df, trend_df


# --- PAGE SETTINGS ---
st.set_page_config(page_title="HuffPost News Dashboard", layout="wide")

st.title("HuffPost News Dashboard")
st.write("Veri Kaynağı: Kaggle • ETL: Docker + Python • Dashboard: Streamlit")

# --- LOAD DATA ---
category_df, trend_df = load_data()

trend_df["publish_date"] = pd.to_datetime(trend_df["publish_date"], errors="coerce")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filtreler")
selected_category = st.sidebar.multiselect(
    "Kategori Seç:",
    options=category_df["category"].unique(),
    default=category_df["category"].unique()
)

filtered_df = category_df[category_df["category"].isin(selected_category)]

# ============================================================

col1, col2 = st.columns(2)

# --- CATEGORY BAR CHART ---
with col1:
    st.subheader("Kategoriye Göre Haber Dağılımı")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.barh(filtered_df["category"], filtered_df["count"], color="skyblue")
    ax1.set_xlabel("Haber Sayısı")
    ax1.set_ylabel("Kategori")
    plt.tight_layout()
    st.pyplot(fig1)

# --- TREND LINE CHART ---
with col2:
    st.subheader("Haber Sayısı Zaman Serisi (Trend)")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(trend_df["publish_date"], trend_df["count"], color="cyan")
    ax2.set_title("Zaman İçinde Haber Sayısı")
    ax2.set_xlabel("Tarih")
    ax2.set_ylabel("Haber Adedi")
    ax2.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)

# ============================================================

st.subheader("Kategori İstatistikleri Tablosu")
st.dataframe(filtered_df, use_container_width=True)
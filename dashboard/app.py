import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


# --- DATABASE CONNECTION ---
@st.cache_data
def load_data():
    conn = sqlite3.connect("/app/data/news_etl.db")

    category_df = pd.read_sql_query("SELECT * FROM category_stats", conn)

    df_trend = pd.read_sql_query("""
        SELECT date, COUNT(*) AS count
        FROM raw_news
        GROUP BY date
        ORDER BY date ASC
    """, conn)

    conn.close()
    return category_df, df_trend



st.set_page_config(page_title="News Dashboard", layout="wide")

st.title("HuffPost News Dashboard")
st.write("Veri Kaynağı: Kaggle • ETL: Docker + Python • Dashboard: Streamlit")

# --- LOAD DATA ---
category_df, trend_df = load_data()

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
st.subheader("Tarihe Göre Haber Sayısı Trend Grafiği")

fig2, ax2 = plt.subplots(figsize=(10, 5))
trend_df["date"] = pd.to_datetime(trend_df["date"])
ax2.plot(trend_df["date"], trend_df["count"], color="purple")
ax2.set_xlabel("Date")
ax2.set_ylabel("News Count")
ax2.grid(True)
st.pyplot(fig2)

# --- DATA PREVIEW ---
st.subheader("Ham Veri Önizleme")
st.dataframe(filtered_df)

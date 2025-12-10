import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# =====================================================================
#                           DATABASE CONNECTION
# =====================================================================
@st.cache_data
def load_data():
    # Docker network içinden erişim: host = postgres, port = 5432
    engine = create_engine(
        "postgresql://news_user:news_pass@postgres:5432/news_db"
    )

    # Kategori istatistikleri
    category_df = pd.read_sql("SELECT * FROM category_stats", engine)

    # Trend verisi (kategori + tarih bazlı count)
    trend_df = pd.read_sql(
        """
        SELECT category, publish_date, COUNT(*) AS count
        FROM raw_news
        GROUP BY category, publish_date
        ORDER BY publish_date ASC
        """,
        engine,
    )

    # Sentiment verisi
    sentiment_df = pd.read_sql(
        """
        SELECT category, sentiment_label
        FROM sentiment_news
        """,
        engine,
    )

    return category_df, trend_df, sentiment_df


# =====================================================================
#                           PAGE SETTINGS
# =====================================================================
st.set_page_config(page_title="HuffPost News Dashboard", layout="wide")

st.title("HuffPost News Dashboard")
st.write("Veri Kaynağı: Kaggle • ETL: Docker + PostgreSQL • Dashboard: Streamlit")


# =====================================================================
#                           LOAD DATA
# =====================================================================
category_df, trend_df, sentiment_df = load_data()
trend_df["publish_date"] = pd.to_datetime(trend_df["publish_date"], errors="coerce")


# =====================================================================
#                           SIDEBAR FILTERS
# =====================================================================
st.sidebar.header("Filtreler")

selected_category = st.sidebar.multiselect(
    "Kategori Seç:",
    options=category_df["category"].unique(),
    default=category_df["category"].unique(),
)

time_resolution = st.sidebar.selectbox(
    "Zaman Çözünürlüğü:",
    ["Günlük", "Aylık", "Yıllık"],
)

# Filtrelenmiş data
filtered_df = category_df[category_df["category"].isin(selected_category)]
trend_filtered = trend_df[trend_df["category"].isin(selected_category)]
sentiment_filtered = sentiment_df[sentiment_df["category"].isin(selected_category)]


# =====================================================================
#                   2 SÜTUNLU KART LAYOUT
# =====================================================================

# Trend verisini önce hazırla (tüm kartlar için gerekli)
trend_tmp = trend_filtered.copy()
trend_tmp["publish_date"] = pd.to_datetime(trend_tmp["publish_date"])
trend_tmp = trend_tmp.set_index("publish_date")

if time_resolution == "Aylık":
    trend_tmp = (
        trend_tmp.groupby("category")
        .resample("M")["count"]
        .sum()
        .reset_index()
    )
elif time_resolution == "Yıllık":
    trend_tmp = (
        trend_tmp.groupby("category")
        .resample("Y")["count"]
        .sum()
        .reset_index()
    )
else:
    trend_tmp = trend_filtered.copy()
    trend_tmp["publish_date"] = pd.to_datetime(trend_tmp["publish_date"])

# İLK SATIR: Kategori Dağılımı ve Zaman Serisi
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown("**📊 Kategori Dağılımı**")
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.barh(filtered_df["category"], filtered_df["count"], color="skyblue")
        ax1.set_xlabel("Haber Sayısı", fontsize=10)
        ax1.set_ylabel("Kategori", fontsize=10)
        ax1.tick_params(labelsize=9)
        plt.tight_layout()
        st.pyplot(fig1, use_container_width=True)

with col2:
    with st.container():
        st.markdown("**📈 Zaman Serisi**")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        if "category" in trend_tmp.columns:
            for cat in selected_category:
                cat_df = trend_tmp[trend_tmp["category"] == cat].copy()
                if not cat_df.empty:
                    if "publish_date" in cat_df.columns:
                        ax2.plot(cat_df["publish_date"], cat_df["count"], label=cat, linewidth=2)
                    else:
                        ax2.plot(range(len(cat_df)), cat_df["count"], label=cat, linewidth=2)
        ax2.set_xlabel("Tarih", fontsize=10)
        ax2.set_ylabel("Haber Sayısı", fontsize=10)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(labelsize=9)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)

# İKİNCİ SATIR: Duygu Analizi ve En Yoğun Günler
col3, col4 = st.columns(2)

with col3:
    with st.container():
        st.markdown("**😊 Duygu Analizi**")
        if not sentiment_filtered.empty:
            sent_cnt = (
                sentiment_filtered.groupby(["category", "sentiment_label"])
                .size()
                .reset_index(name="count")
            )
            fig_s, ax_s = plt.subplots(figsize=(12, 6))
            colors = {"Positive": "green", "Neutral": "gray", "Negative": "red"}
            for s in ["Positive", "Neutral", "Negative"]:
                subset = sent_cnt[sent_cnt["sentiment_label"] == s]
                if not subset.empty:
                    ax_s.bar(subset["category"], subset["count"], label=s, color=colors[s])
            ax_s.set_xlabel("Kategori", fontsize=10)
            ax_s.set_ylabel("Haber Sayısı", fontsize=10)
            ax_s.legend(fontsize=9)
            ax_s.tick_params(labelsize=8)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_s, use_container_width=True)
        else:
            st.info("Duygu analizi verisi bulunamadı.")

with col4:
    with st.container():
        st.markdown("**🔥 En Yoğun Günler**")
        if not trend_filtered.empty:
            top_days = (
                trend_filtered.groupby("publish_date")["count"]
                .sum()
                .reset_index()
                .sort_values("count", ascending=False)
                .head(10)
            )
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            ax3.bar(top_days["publish_date"].dt.strftime("%Y-%m-%d"), top_days["count"], color="orange")
            ax3.set_xlabel("Tarih", fontsize=10)
            ax3.set_ylabel("Haber Sayısı", fontsize=10)
            ax3.tick_params(labelsize=9)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig3, use_container_width=True)
        else:
            st.info("Veri bulunamadı.")


# ÜÇÜNCÜ SATIR: Kelime Bulutu (Tam Genişlik)
st.markdown("---")
st.markdown("**☁️ Kelime Bulutu**")

# Word cloud için tekrar engine oluştur
engine_wc = create_engine(
    "postgresql://news_user:news_pass@postgres:5432/news_db"
)
df_wc = pd.read_sql("SELECT category, headline FROM raw_news", engine_wc)
df_wc = df_wc[df_wc["category"].isin(selected_category)]

if not df_wc.empty:
    from wordcloud import WordCloud, STOPWORDS
    
    # Ana kelime bulutu görünümü
    text = " ".join(df_wc["headline"].astype(str))
    wc = WordCloud(width=1200, height=600, background_color="white", 
                  stopwords=set(STOPWORDS), max_words=200).generate(text)
    fig_wc, ax_wc = plt.subplots(figsize=(14, 7))
    ax_wc.imshow(wc, interpolation="bilinear")
    ax_wc.axis("off")
    plt.tight_layout()
    st.pyplot(fig_wc, use_container_width=True)
    
    # Bilgi paneli
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("Toplam Kelime", len(text.split()))
    with col_info2:
        st.metric("Kategori Sayısı", len(selected_category))
    with col_info3:
        st.metric("Toplam Haber", len(df_wc))
else:
    st.info("Kelime bulutu için veri bulunamadı.")
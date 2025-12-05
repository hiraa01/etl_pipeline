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
#                           CARD LAYOUT - GRAFİKLER ALT ALTA
# =====================================================================

# ---------------------- CATEGORY CHART (Kart 1) ----------------------
    st.markdown("**📊 Kategori Dağılımı**")
    # Küçük önizleme (her zaman görünür)
    fig1_small, ax1_small = plt.subplots(figsize=(2.5, 2.5))
    top_5 = filtered_df.head(5)
    # Kategori isimlerini kısalt (maksimum 8 karakter)
    labels = [cat[:8] + ".." if len(cat) > 8 else cat for cat in top_5["category"]]
    ax1_small.barh(range(len(top_5)), top_5["count"], color="skyblue")
    ax1_small.set_yticks(range(len(top_5)))
    ax1_small.set_yticklabels(labels, fontsize=5)
    ax1_small.set_xlabel("", fontsize=0)
    ax1_small.set_ylabel("", fontsize=0)
    ax1_small.tick_params(labelsize=5, pad=0.5)
    ax1_small.tick_params(axis='x', labelsize=5)
    # X eksen sayılarını kaldır
    ax1_small.set_xticks([])
    plt.tight_layout(pad=0.3)
    st.pyplot(fig1_small, use_container_width=True)
    
    # Büyük versiyon (expander içinde)
    with st.expander("🔍 Detaylı Görünüm", expanded=False):
        st.markdown("**Kategoriye Göre Haber Dağılımı**")
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        ax1.barh(filtered_df["category"], filtered_df["count"], color="skyblue")
        ax1.set_xlabel("Haber Sayısı")
        ax1.set_ylabel("Kategori")
        plt.tight_layout()
        st.pyplot(fig1)

# ---------------------- TREND CHART (Kart 2) ----------------------
    st.markdown("**📈 Zaman Serisi**")
    # Trend verisini hazırla
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
    
    # Küçük önizleme (her zaman görünür)
    fig2_small, ax2_small = plt.subplots(figsize=(2.5, 2.5))
    if len(selected_category) > 0 and not trend_tmp.empty:
        first_cat = selected_category[0]
        if "category" in trend_tmp.columns:
            cat_df = trend_tmp[trend_tmp["category"] == first_cat].copy()
            if not cat_df.empty:
                if "publish_date" in cat_df.columns:
                    ax2_small.plot(cat_df["publish_date"], cat_df["count"], color="blue", linewidth=1)
                else:
                    ax2_small.plot(range(len(cat_df)), cat_df["count"], color="blue", linewidth=1)
    ax2_small.set_xlabel("", fontsize=0)
    ax2_small.set_ylabel("", fontsize=0)
    ax2_small.tick_params(labelsize=5, pad=1)
    # X eksen etiketlerini kaldır veya çok az göster
    ax2_small.set_xticks([])
    ax2_small.set_xticklabels([])
    plt.tight_layout(pad=0.5)
    st.pyplot(fig2_small, use_container_width=True)
    
    # Büyük versiyon (expander içinde)
    with st.expander("🔍 Detaylı Görünüm", expanded=False):
        st.markdown("**Zaman Serisi (Kategori Bazlı)**")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        if "category" in trend_tmp.columns:
            for cat in selected_category:
                cat_df = trend_tmp[trend_tmp["category"] == cat].copy()
                if not cat_df.empty:
                    if "publish_date" in cat_df.columns:
                        ax2.plot(cat_df["publish_date"], cat_df["count"], label=cat)
                    else:
                        ax2.plot(range(len(cat_df)), cat_df["count"], label=cat)
        ax2.set_xlabel("Tarih")
        ax2.set_ylabel("Haber Sayısı")
        ax2.legend(fontsize=8)
        ax2.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)

# ---------------------- SENTIMENT CHART (Kart 3) ----------------------
    st.markdown("**😊 Duygu Analizi**")
    if not sentiment_filtered.empty:
        sent_cnt = (
            sentiment_filtered.groupby(["category", "sentiment_label"])
            .size()
            .reset_index(name="count")
        )
        
        # Küçük önizleme (her zaman görünür)
        fig_s_small, ax_s_small = plt.subplots(figsize=(2.5, 2.5))
        sent_summary = sent_cnt.groupby("sentiment_label")["count"].sum()
        colors_small = {"Positive": "green", "Neutral": "gray", "Negative": "red"}
        # Etiketleri kısalt
        labels_short = [lbl[:3] for lbl in sent_summary.index]
        ax_s_small.bar(range(len(sent_summary)), sent_summary.values, 
                      color=[colors_small.get(x, "blue") for x in sent_summary.index])
        ax_s_small.set_xticks(range(len(sent_summary)))
        ax_s_small.set_xticklabels(labels_short, fontsize=5)
        ax_s_small.set_ylabel("", fontsize=0)
        ax_s_small.tick_params(labelsize=5, pad=1)
        plt.tight_layout(pad=0.5)
        st.pyplot(fig_s_small, use_container_width=True)
        
        # Büyük versiyon (expander içinde)
        with st.expander("🔍 Detaylı Görünüm", expanded=False):
            st.markdown("**Kategori Bazlı Duygu Dağılımı**")
            fig_s, ax_s = plt.subplots(figsize=(12, 6))
            colors = {"Positive": "green", "Neutral": "gray", "Negative": "red"}
            for s in ["Positive", "Neutral", "Negative"]:
                subset = sent_cnt[sent_cnt["sentiment_label"] == s]
                if not subset.empty:
                    ax_s.bar(subset["category"], subset["count"], label=s, color=colors[s])
            ax_s.set_xlabel("Kategori")
            ax_s.set_ylabel("Haber Sayısı")
            ax_s.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig_s)
    else:
        st.info("Duygu analizi verisi bulunamadı.")

# ---------------------- TOP 10 DAYS (Kart 4) ----------------------
    st.markdown("**🔥 En Yoğun Günler**")
    if not trend_filtered.empty:
        top_days = (
            trend_filtered.groupby("publish_date")["count"]
            .sum()
            .reset_index()
            .sort_values("count", ascending=False)
            .head(10)
        )
        
        # Küçük önizleme (her zaman görünür)
        fig3_small, ax3_small = plt.subplots(figsize=(2.5, 2.5))
        top_5_days = top_days.head(5)
        ax3_small.bar(range(len(top_5_days)), top_5_days["count"], color="orange")
        ax3_small.set_ylabel("", fontsize=0)
        ax3_small.set_xlabel("", fontsize=0)
        ax3_small.set_xticks([])
        ax3_small.set_xticklabels([])
        ax3_small.tick_params(labelsize=5, pad=1)
        plt.tight_layout(pad=0.5)
        st.pyplot(fig3_small, use_container_width=True)
        
        # Büyük versiyon (expander içinde)
        with st.expander("🔍 Detaylı Görünüm", expanded=False):
            st.markdown("**En Çok Haber Üretilen 10 Gün**")
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            ax3.bar(top_days["publish_date"].dt.strftime("%Y-%m-%d"), top_days["count"], color="orange")
            ax3.set_xlabel("Tarih")
            ax3.set_ylabel("Haber Sayısı")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig3)
    else:
        st.info("Veri bulunamadı.")


# =====================================================================
#                        WORD CLOUD (Kart 5)
# =====================================================================
st.markdown("---")

# Word cloud için tekrar engine oluştur
engine_wc = create_engine(
    "postgresql://news_user:news_pass@postgres:5432/news_db"
)
df_wc = pd.read_sql("SELECT category, headline FROM raw_news", engine_wc)
df_wc = df_wc[df_wc["category"].isin(selected_category)]

if not df_wc.empty:
    from wordcloud import WordCloud, STOPWORDS
    
    st.markdown("**☁️ Kelime Bulutu**")
    # Küçük önizleme (her zaman görünür) - aynı boyutta
    text_preview = " ".join(df_wc["headline"].astype(str).head(100))
    wc_small = WordCloud(width=200, height=200, background_color="white", 
                        stopwords=set(STOPWORDS), max_words=30, 
                        relative_scaling=0.5, font_step=1).generate(text_preview)
    fig_wc_small, ax_wc_small = plt.subplots(figsize=(2.5, 2.5))
    ax_wc_small.imshow(wc_small, interpolation="bilinear")
    ax_wc_small.axis("off")
    plt.tight_layout(pad=0.5)
    st.pyplot(fig_wc_small, use_container_width=True)
    
    # Büyük versiyon (expander içinde)
    with st.expander("🔍 Detaylı Görünüm", expanded=False):
        st.markdown("**Kelime Bulutu**")
        text = " ".join(df_wc["headline"].astype(str))
        wc = WordCloud(width=1200, height=600, background_color="white", 
                      stopwords=set(STOPWORDS), max_words=200).generate(text)
        fig_wc, ax_wc = plt.subplots(figsize=(14, 7))
        ax_wc.imshow(wc, interpolation="bilinear")
        ax_wc.axis("off")
        st.pyplot(fig_wc)
else:
    st.info("Kelime bulutu için veri bulunamadı.")
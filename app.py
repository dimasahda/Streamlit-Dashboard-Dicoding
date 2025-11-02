# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ===============================
# Konfigurasi Dashboard
# ===============================
st.set_page_config(page_title="Olist E-Commerce Dashboard", layout="wide")

st.title("📊 Olist E-Commerce Dashboard")
st.markdown("""
Dashboard ini dibuat untuk menjawab dua pertanyaan bisnis utama:
1. Bagaimana pola performa penjualan dari waktu ke waktu?
2. Faktor apa yang berpengaruh terhadap kepuasan pelanggan (terutama waktu pengiriman)?
""")

# ===============================
# Load Data
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("olist_cleaned_dataset.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'olist_merged_cleaned.csv' tidak ditemukan.")
    st.stop()

# ===============================
# Preprocessing dasar
# ===============================
# Konversi kolom tanggal
date_cols = [col for col in df.columns if "date" in col or "timestamp" in col]
for col in date_cols:
    try:
        df[col] = pd.to_datetime(df[col])
    except Exception:
        pass

# Pastikan ada kolom harga dan rating
if 'price' not in df.columns:
    st.error("Kolom 'price' tidak ditemukan di dataset.")
    st.stop()

if 'review_score' not in df.columns:
    st.error("Kolom 'review_score' tidak ditemukan di dataset.")
    st.stop()

# ===============================
# Tabs untuk Pertanyaan Bisnis
# ===============================
tab1, tab2 = st.tabs([
    "Tren Penjualan dari Waktu ke Waktu",
    "Hubungan Waktu Pengiriman & Kepuasan Pelanggan"
])

# ======================================================
# TAB 1: Tren Penjualan
# ======================================================
with tab1:
    st.header("Bagaimana Pola Performa Penjualan dari Waktu ke Waktu?")

    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['order_year_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)

    sales_trend = (
        df.groupby('order_year_month')
        .agg(total_sales=('price', 'sum'),
             total_orders=('order_id', 'nunique'))
        .reset_index()
    )

    # Plot penjualan
    fig, ax1 = plt.subplots(figsize=(12, 5))
    sns.lineplot(x='order_year_month', y='total_sales', data=sales_trend, color='tab:blue', marker='o', label='Total Sales (BRL)', ax=ax1)
    ax1.set_ylabel('Total Sales (BRL)', color='tab:blue')
    ax1.set_xlabel('Tahun-Bulan')
    plt.xticks(rotation=45)

    ax2 = ax1.twinx()
    sns.lineplot(x='order_year_month', y='total_orders', data=sales_trend, color='tab:orange', marker='o', label='Total Orders', ax=ax2)
    ax2.set_ylabel('Jumlah Pesanan', color='tab:orange')

    plt.title("Tren Penjualan dan Jumlah Pesanan dari Waktu ke Waktu")
    st.pyplot(fig)

    st.markdown("""
    **Insight Bisnis:**
    - Pola kenaikan dan penurunan penjualan dapat mengindikasikan musim puncak belanja (peak season).
    - Kombinasi antara jumlah pesanan dan total pendapatan menunjukkan **seberapa besar nilai rata-rata per pesanan**.
    """)

    # Produk terlaris
    st.subheader("Kategori Produk Terlaris")
    if "product_category_name" in df.columns:
        top_categories = (
            df.groupby('product_category_name')['price']
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        fig2, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=top_categories.values, y=top_categories.index, palette="viridis", ax=ax)
        ax.set_xlabel("Total Penjualan (BRL)")
        ax.set_ylabel("Kategori Produk")
        plt.title("Top 10 Kategori Produk dengan Penjualan Tertinggi")
        st.pyplot(fig2)

        st.markdown("""
        **Insight Bisnis:**
        - Kategori terlaris dapat menjadi fokus promosi dan pengelolaan stok.
        - Kategori dengan margin tinggi bisa dijadikan prioritas dalam strategi harga.
        """)

# ======================================================
# TAB 2: Delivery Time vs Review Score
# ======================================================
with tab2:
    st.header("Hubungan antara Waktu Pengiriman dan Kepuasan Pelanggan")

    if all(col in df.columns for col in ["order_delivered_customer_date", "order_purchase_timestamp", "review_score"]):
        df["delivery_time_days"] = (
            df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
        ).dt.days

        fig3, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(x="review_score", y="delivery_time_days", data=df, palette="coolwarm", ax=ax)
        ax.set_title("Distribusi Waktu Pengiriman per Skor Review")
        ax.set_xlabel("Skor Review (1–5)")
        ax.set_ylabel("Waktu Pengiriman (hari)")
        st.pyplot(fig3)

        corr = df[["delivery_time_days", "review_score"]].corr().iloc[0, 1]
        st.metric("Korelasi Delivery Time vs Review Score", f"{corr:.2f}")

        st.markdown("""
        **Insight Bisnis:**
        - Skor review cenderung **menurun** ketika waktu pengiriman lebih lama.
        - Korelasi negatif antara waktu pengiriman dan review score menunjukkan pentingnya efisiensi logistik.
        - Mengurangi waktu pengiriman bisa menjadi strategi untuk meningkatkan kepuasan pelanggan.
        """)
    else:
        st.warning("Kolom waktu pengiriman tidak tersedia di dataset.")

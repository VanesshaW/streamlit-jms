import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Penjualan & Stok", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Dashboard Penjualan Distributor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Analisis data penjualan, stok produk, dan performa bulanan</p>", unsafe_allow_html=True)

# Navigasi
st.sidebar.header("🧭 Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["Dashboard Penjualan", "Manajemen Stok", "Forecasting"])

# Upload file
uploaded_file = st.sidebar.file_uploader("📤 Upload File Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Cleaning data
    df['tanggal_transaksi'] = pd.to_datetime(df['tanggal_transaksi'], errors='coerce')
    df['total_harga'] = pd.to_numeric(df['total_harga'], errors='coerce')
    df['jumlah'] = pd.to_numeric(df['jumlah'], errors='coerce')

    # Dummy filter
    st.sidebar.subheader("🔎 Filter Data")
    kategori_filter = st.sidebar.multiselect("Pilih Kategori Produk", options=df['kategori'].unique(), default=df['kategori'].unique())
    df = df[df['kategori'].isin(kategori_filter)]

    if menu == "Dashboard Penjualan":
        st.subheader("📈 Ringkasan Penjualan")

        # Ringkasan nilai
        total_penjualan = df['total_harga'].sum()
        total_transaksi = len(df)
        produk_terjual = df['jumlah'].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Penjualan", f"Rp {total_penjualan:,.0f}")
        col2.metric("📦 Produk Terjual", f"{produk_terjual}")
        col3.metric("🧾 Jumlah Transaksi", f"{total_transaksi}")

        # Agregasi bulanan
        df_bulan = df.groupby(df['tanggal_transaksi'].dt.to_period('M')).agg({
            'total_harga': 'sum',
            'jumlah': 'sum'
        }).reset_index()
        df_bulan['tanggal_transaksi'] = df_bulan['tanggal_transaksi'].dt.to_timestamp()

        # Grafik 1: Line Chart Penjualan
        st.markdown("### 📊 Total Penjualan per Bulan")
        fig1 = px.line(df_bulan, x='tanggal_transaksi', y='total_harga',
                       markers=True, title="Tren Penjualan", color_discrete_sequence=['#4e79a7'])
        st.plotly_chart(fig1, use_container_width=True)

        # Grafik 2: Bar Chart Produk Terjual
        st.markdown("### 📦 Jumlah Produk Terjual per Bulan")
        fig2 = px.bar(df_bulan, x='tanggal_transaksi', y='jumlah',
                      title="Volume Penjualan", color_discrete_sequence=['#f28e2b'])
        st.plotly_chart(fig2, use_container_width=True)

    elif menu == "Manajemen Stok":
        st.subheader("📦 Manajemen Stok Sederhana")
        stok = df.groupby(['produk', 'kategori', 'merek'])['jumlah'].sum().reset_index()
        stok = stok.sort_values(by='jumlah', ascending=False)
        st.dataframe(stok, use_container_width=True)

    elif menu == "Forecasting":
        st.subheader("🔮 Forecasting Penjualan")
        st.info("Akan ditambahkan fitur forecasting di tahap selanjutnya (Prophet atau Moving Average).")

else:
    st.warning("⬆️ Upload file Excel terlebih dahulu untuk melihat dashboard.")

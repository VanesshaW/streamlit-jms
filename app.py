import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Penjualan & Stok", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Dashboard Penjualan Distributor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Analisis data penjualan, stok produk, dan performa bulanan</p>", unsafe_allow_html=True)

# Sidebar Navigasi
st.sidebar.header("🧭 Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["Dashboard Penjualan", "Manajemen Stok", "Forecasting"])

# Upload file Excel
uploaded_file = st.sidebar.file_uploader("📤 Upload File Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Cleaning data
    df['tanggal_transaksi'] = pd.to_datetime(df['tanggal_transaksi'], errors='coerce')
    df['total_harga'] = pd.to_numeric(df['total_harga'], errors='coerce')
    df['jumlah'] = pd.to_numeric(df['jumlah'], errors='coerce')

    # Filter kategori produk
    st.sidebar.subheader("🔎 Filter Data")
    kategori_filter = st.sidebar.multiselect("Pilih Kategori Produk", options=df['kategori'].unique(), default=df['kategori'].unique())
    df = df[df['kategori'].isin(kategori_filter)]

    if menu == "Dashboard Penjualan":
        st.subheader("📈 Ringkasan Penjualan")

        # Ringkasan metrik
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

        # Grafik 1: Total Penjualan per Bulan
        st.markdown("### 📊 Total Penjualan per Bulan")
        fig1 = px.line(df_bulan, x='tanggal_transaksi', y='total_harga',
                       markers=True, title="Tren Penjualan",
                       color_discrete_sequence=['#4e79a7'])
        st.plotly_chart(fig1, use_container_width=True)

        # Grafik 2: Jumlah Produk Terjual
        st.markdown("### 📦 Jumlah Produk Terjual per Bulan")
        fig2 = px.bar(df_bulan, x='tanggal_transaksi', y='jumlah',
                      title="Volume Penjualan",
                      color_discrete_sequence=['#f28e2b'])
        st.plotly_chart(fig2, use_container_width=True)

    elif menu == "Manajemen Stok":
        st.subheader("📦 Manajemen Stok Sederhana")

        stok = df.groupby(['produk', 'kategori', 'merek'])['jumlah'].sum().reset_index()
        stok = stok.sort_values(by='jumlah', ascending=False)
        st.dataframe(stok, use_container_width=True)

        st.markdown("---")
        st.markdown("### ✍️ Simulasi Tambah / Edit Stok (Dummy)")

        with st.form("form_stok"):
            col1, col2 = st.columns(2)
            with col1:
                produk_baru = st.text_input("Nama Produk")
                kategori_baru = st.text_input("Kategori")
                jumlah_baru = st.number_input("Jumlah", min_value=0, step=1)
            with col2:
                merek_baru = st.text_input("Merek")
                ukuran_baru = st.text_input("Ukuran/Spesifikasi")
                harga_baru = st.number_input("Harga Satuan", min_value=0, step=1000)

            submitted = st.form_submit_button("✅ Simpan Stok (Dummy)")

        if submitted:
            st.success(f"✅ Stok untuk produk **{produk_baru}** berhasil ditambahkan (simulasi).")
            st.info("Catatan: Data ini hanya dummy, tidak tersimpan permanen karena tidak menggunakan database.")

    elif menu == "Forecasting":
        st.subheader("🔮 Forecasting Penjualan")
        st.info("📌 Fitur forecasting akan ditambahkan menggunakan Prophet atau moving average.")

else:
    st.warning("⬆️ Upload file Excel terlebih dahulu untuk melihat dashboard.")

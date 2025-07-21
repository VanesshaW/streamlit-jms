import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Aplikasi Penjualan & Stok", layout="wide")

# Sidebar Navigasi
st.sidebar.title("🧭 Navigasi")
menu = st.sidebar.radio("Pilih halaman:", ["📊 Dashboard Penjualan", "📦 Manajemen Stok", "📈 Forecasting"])

# Upload file Excel
uploaded_file = st.sidebar.file_uploader("Upload file Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Pastikan kolom 'bulan_transaksi' berupa datetime
    df['bulan_transaksi'] = pd.to_datetime(df['bulan_transaksi'], errors='coerce')

    # Bersihkan kolom harga jika perlu (hilangkan Rp, koma, dll)
    df['total_harga'] = df['total_harga'].replace('[Rp., ]', '', regex=True).astype(float)
    df['jumlah'] = pd.to_numeric(df['jumlah'], errors='coerce')

    if menu == "📊 Dashboard Penjualan":
        st.title("📊 Dashboard Penjualan")

        # Total penjualan per bulan
        df_bulan = df.groupby(df['bulan_transaksi'].dt.to_period('M')).agg({
            'total_harga': 'sum',
            'jumlah': 'sum'
        }).reset_index()
        df_bulan['bulan_transaksi'] = df_bulan['bulan_transaksi'].dt.to_timestamp()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Total Penjualan per Bulan (Rp)")
            fig_line = px.line(df_bulan, x='bulan_transaksi', y='total_harga', markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
        with col2:
            st.subheader("Jumlah Produk Terjual per Bulan")
            fig_bar = px.bar(df_bulan, x='bulan_transaksi', y='jumlah')
            st.plotly_chart(fig_bar, use_container_width=True)

    elif menu == "📦 Manajemen Stok":
        st.title("📦 Manajemen Stok")

        stok = df.groupby(['produk', 'kategori', 'merek'])['jumlah'].sum().reset_index()
        stok = stok.sort_values(by='jumlah', ascending=False)
        st.dataframe(stok, use_container_width=True)

    elif menu == "📈 Forecasting":
        st.title("📈 Forecasting Penjualan")
        st.write("Akan menggunakan Prophet atau moving average... (dalam pengembangan)")

else:
    st.warning("⬆️ Silakan upload file Excel penjualan terlebih dahulu.")

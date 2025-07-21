import streamlit as st
import pandas as pd

st.set_page_config(page_title="Aplikasi Penjualan & Stok", layout="wide")

# Sidebar Navigasi
st.sidebar.title("🧭 Navigasi")
menu = st.sidebar.radio("Pilih halaman:", ["📊 Dashboard Penjualan", "📦 Manajemen Stok", "📈 Forecasting"])

# Upload file Excel
uploaded_file = st.sidebar.file_uploader("Upload file Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['bulan_transaksi'] = pd.to_datetime(df['bulan_transaksi'], errors='coerce')

    if menu == "📊 Dashboard Penjualan":
        st.title("📊 Dashboard Penjualan")
        st.write("Menampilkan ringkasan penjualan berdasarkan data yang diunggah.")

        # Contoh chart total penjualan per bulan
        df_bulan = df.groupby(df['bulan_transaksi'].dt.to_period('M')).sum(numeric_only=True).reset_index()
        df_bulan['bulan_transaksi'] = df_bulan['bulan_transaksi'].dt.to_timestamp()

        st.line_chart(df_bulan.set_index('bulan_transaksi')['total_harga'])
        st.bar_chart(df_bulan.set_index('bulan_transaksi')['jumlah'])

    elif menu == "📦 Manajemen Stok":
        st.title("📦 Manajemen Stok Sederhana")
        stok = df.groupby('produk')['jumlah'].sum().reset_index()
        st.dataframe(stok)

    elif menu == "📈 Forecasting":
        st.title("📈 Forecasting Penjualan")
        st.write("Gunakan Prophet atau Moving Average (akan ditambahkan).")
        # Nanti kita tambahkan model forecasting-nya

else:
    st.warning("⬆️ Silakan upload file Excel penjualan terlebih dahulu.")


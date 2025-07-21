import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from prophet.plot import plot_plotly

st.set_page_config(page_title="Dashboard Penjualan", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Dashboard Penjualan</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Analisis penjualan, stok produk, dan prediksi permintaan</p>", unsafe_allow_html=True)

st.sidebar.header("🧭 Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["Dashboard Penjualan", "Manajemen Stok", "Forecasting"])

uploaded_file = st.sidebar.file_uploader("📤 Upload File Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['tanggal_transaksi'] = pd.to_datetime(df['tanggal_transaksi'], errors='coerce')
    df['total_harga'] = pd.to_numeric(df['total_harga'], errors='coerce')
    df['jumlah'] = pd.to_numeric(df['jumlah'], errors='coerce')

    st.sidebar.subheader("🔎 Filter Data")
    kategori_filter = st.sidebar.multiselect("Pilih Kategori Produk", options=df['kategori'].unique(), default=df['kategori'].unique())
    df = df[df['kategori'].isin(kategori_filter)]

    if menu == "Dashboard Penjualan":
        st.subheader("📈 Ringkasan Penjualan")
        total_penjualan = df['total_harga'].sum()
        produk_terjual = df['jumlah'].sum()
        total_transaksi = len(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Penjualan", f"Rp {total_penjualan:,.0f}")
        col2.metric("📦 Produk Terjual", f"{produk_terjual}")
        col3.metric("🧾 Transaksi", f"{total_transaksi}")

        df_bulan = df.groupby(df['tanggal_transaksi'].dt.to_period('M')).agg({
            'total_harga': 'sum', 'jumlah': 'sum'
        }).reset_index()
        df_bulan['tanggal_transaksi'] = df_bulan['tanggal_transaksi'].dt.to_timestamp()

        st.markdown("### 📊 Total Penjualan per Bulan")
        fig1 = px.line(df_bulan, x='tanggal_transaksi', y='total_harga',
                       markers=True, title="Tren Penjualan", color_discrete_sequence=['#4e79a7'])
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("### 📦 Jumlah Produk Terjual per Bulan")
        fig2 = px.bar(df_bulan, x='tanggal_transaksi', y='jumlah',
                      title="Volume Penjualan", color_discrete_sequence=['#f28e2b'])
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

    elif menu == "Forecasting":
        st.subheader("🔮 Forecasting Penjualan Bulanan")
        df_bulanan = df.groupby(df['tanggal_transaksi'].dt.to_period('M')).agg({'total_harga': 'sum'}).reset_index()
        df_bulanan['ds'] = df_bulanan['tanggal_transaksi'].dt.to_timestamp()
        df_bulanan['y'] = df_bulanan['total_harga']
        df_bulanan = df_bulanan[['ds', 'y']]

        st.write("Data Historis:")
        st.dataframe(df_bulanan.tail(), use_container_width=True)

        m = Prophet()
        m.fit(df_bulanan)
        future = m.make_future_dataframe(periods=6, freq='M')
        forecast = m.predict(future)

        st.markdown("### 📈 Forecast Penjualan Total")
        fig3 = plot_plotly(m, forecast)
        st.plotly_chart(fig3, use_container_width=True)

        avg_pred = forecast.tail(6)['yhat'].mean()
        st.success(f"Rata-rata prediksi penjualan 6 bulan ke depan: **Rp {avg_pred:,.0f}**")

        st.markdown("## 🌟 Forecast Produk Terlaris (Top 5)")
        top5_produk = df.groupby('produk')['jumlah'].sum().sort_values(ascending=False).head(5).index.tolist()

        for produk in top5_produk:
            df_produk = df[df['produk'] == produk]
            df_bulanan_produk = df_produk.groupby(df_produk['tanggal_transaksi'].dt.to_period('M'))['jumlah'].sum().reset_index()
            df_bulanan_produk['ds'] = df_bulanan_produk['tanggal_transaksi'].dt.to_timestamp()
            df_bulanan_produk['y'] = df_bulanan_produk['jumlah']
            df_bulanan_produk = df_bulanan_produk[['ds', 'y']]

            st.markdown(f"### 🔧 Forecast: {produk}")
            if len(df_bulanan_produk) >= 6:
                m_produk = Prophet()
                m_produk.fit(df_bulanan_produk)
                future_produk = m_produk.make_future_dataframe(periods=6, freq='M')
                forecast_produk = m_produk.predict(future_produk)
                fig_produk = plot_plotly(m_produk, forecast_produk)
                st.plotly_chart(fig_produk, use_container_width=True)

                pred = forecast_produk.tail(6)['yhat'].mean()
                st.info(f"📌 Estimasi permintaan 6 bulan ke depan: **{pred:.0f} unit**")
            else:
                st.warning("⚠️ Data penjualan terlalu sedikit untuk forecasting.")
else:
    st.warning("⬆️ Upload file Excel terlebih dahulu.")

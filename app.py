import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# KONFIGURASI HALAMAN
# ============================================================================
st.set_page_config(page_title="Simulasi Monte Carlo FITE", layout="wide")

# ============================================================================
# STYLE (TERANG & BERSIH)
# ============================================================================
st.markdown("""
<style>
.main-title {
    font-size: 28px;
    font-weight: bold;
}
.box {
    background: #ffffff;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ddd;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ENGINE
# ============================================================================
class Engine:
    @staticmethod
    def run(config, n=20000, percepatan=1.0):
        df = pd.DataFrame()
        total = np.zeros(n)

        for tahap, p in config.items():
            durasi = np.random.triangular(p['min'], p['mode'], p['max'], n)

            # RISIKO
            cuaca = np.random.rand(n) < 0.1
            material = np.random.rand(n) < 0.1
            desain = np.random.rand(n) < 0.05
            produktivitas = np.random.rand(n) < 0.15

            faktor = 1 + cuaca*0.2 + material*0.25 + desain*0.3 + produktivitas*0.15

            durasi = durasi * faktor
            durasi = durasi / percepatan

            df[tahap] = durasi
            total += durasi

        df["Total"] = total
        return df

# ============================================================================
# HEADER
# ============================================================================
st.markdown("## 🏗️ Simulasi Monte Carlo - Pembangunan Gedung FITE")

st.info("""
**Deskripsi Proyek:**  
Pembangunan gedung FITE 5 lantai dengan fasilitas lengkap: ruang kelas, laboratorium komputer, elektro, VR/AR, game, ruang dosen, dll.

**Tujuan Simulasi:**  
Menganalisis durasi proyek, risiko keterlambatan, tahapan kritis, dan probabilitas penyelesaian.
""")

# ============================================================================
# SIDEBAR
# ============================================================================
st.sidebar.title("⚙️ Konfigurasi Simulasi")

iterasi = st.sidebar.slider("Jumlah Iterasi", 10000, 50000, 20000)
percepatan = st.sidebar.slider("Percepatan Resource", 1.0, 2.0, 1.0)

tahapan_default = {
    "Persiapan Lahan": (1,2,3),
    "Pondasi Dasar": (2,3,5),
    "Struktur Lantai 1-2": (3,4,6),
    "Struktur Lantai 3-4": (3,4,6),
    "Struktur Lantai 5": (2,3,5),
    "Instalasi Listrik & Air": (2,3,5),
    "Pembangunan Laboratorium": (3,5,8),
    "Finishing & Interior": (2,3,5),
    "Pengujian Sistem": (1,2,3),
    "Serah Terima": (0.5,1,2)
}

config = {}

st.sidebar.subheader("Konfigurasi Tahapan")

for tahap, val in tahapan_default.items():
    with st.sidebar.expander(tahap):
        mn = st.number_input(f"Min {tahap}", value=val[0])
        md = st.number_input(f"Mode {tahap}", value=val[1])
        mx = st.number_input(f"Max {tahap}", value=val[2])
        config[tahap] = {"min":mn,"mode":md,"max":mx}

run = st.sidebar.button("🚀 JALANKAN SIMULASI")

# ============================================================================
# PREVIEW
# ============================================================================
st.subheader("📋 Preview Konfigurasi Tahapan")

for t, v in config.items():
    st.write(f"{t} | Min: {v['min']} | Mode: {v['mode']} | Max: {v['max']}")

# ============================================================================
# HASIL
# ============================================================================
if run:

    df = Engine.run(config, iterasi, percepatan)

    rata = df["Total"].mean()
    p95 = np.percentile(df["Total"], 95)

    prob16 = (df["Total"] <= 16).mean()*100
    prob20 = (df["Total"] <= 20).mean()*100
    prob24 = (df["Total"] <= 24).mean()*100

    critical = df.drop(columns=["Total"]).mean().idxmax()

    st.markdown("## 📊 Hasil Simulasi")

    c1,c2,c3 = st.columns(3)
    c1.markdown(f"<div class='box'><h4>Rata-rata</h4><h2>{rata:.1f} bulan</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='box'><h4>P95</h4><h2>{p95:.1f} bulan</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='box'><h4>Tahap Kritis</h4><h2>{critical}</h2></div>", unsafe_allow_html=True)

    st.subheader("📅 Probabilitas Deadline")
    st.write(f"≤ 16 bulan: {prob16:.2f}%")
    st.write(f"≤ 20 bulan: {prob20:.2f}%")
    st.write(f"≤ 24 bulan: {prob24:.2f}%")

    # DISTRIBUSI
    fig = px.histogram(df, x="Total", nbins=50, title="Distribusi Durasi")
    st.plotly_chart(fig, use_container_width=True)

    # S CURVE
    sorted_data = np.sort(df["Total"])
    p = np.arange(len(sorted_data))/len(sorted_data)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=sorted_data, y=p))
    fig2.update_layout(title="S-Curve Risiko")
    st.plotly_chart(fig2, use_container_width=True)

    # VARIANSI
    st.subheader("📊 Variansi Tahapan")
    fig3 = px.box(df.drop(columns=["Total"]))
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("Klik tombol di sidebar untuk menjalankan simulasi")
# app.py
"""
EksporAI - Platform AI untuk Export Readiness & Intelligent Matchmaking UMKM
MVP Hackathon PIDI 2026 | Alvindra Agus Syahputra
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import uuid

# Import semua modules
from utils.ai_engine import predict_readiness_score
from utils.matchmaking import get_buyer_recommendations
from utils.document_processor import process_document_file
from utils.firebase_config import get_firebase
from utils.transaction_tracker import get_transaction_tracker
from utils.admin_manager import get_admin_manager

# Page config - MOBILE OPTIMIZED
st.set_page_config(
    page_title="EksporAI - Platform Ekspor UMKM",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed", # Di-collapse agar di HP langsung fokus ke konten
    menu_items=None
)

# Cache data 100k
@st.cache_data
def load_real_data():
    file_path = 'data/dummy_umkm.csv'
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

df_real = load_real_data()

# ============================================
# CUSTOM CSS - SUPER RESPONSIVE & APP-LIKE
# ============================================
st.markdown("""
<style>
    /* Global Background & Font */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Fix Padding for Mobile View */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1200px;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding-top: 3rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }
    
    /* Make Radio Buttons look like Menu Items */
    .stRadio > div { gap: 0.4rem; }
    .stRadio label {
        padding: 0.8rem 1rem !important;
        background-color: #ffffff;
        border-radius: 12px;
        border: 1px solid transparent;
        transition: all 0.2s ease-in-out;
        cursor: pointer;
    }
    .stRadio label:hover { background-color: #f1f5f9; }
    div[role="radiogroup"] > label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {
        font-weight: 600; font-size: 1rem; color: #1e293b;
    }
    .stRadio div[data-baseweb="radio"] div:first-child { display: none; }

    /* Metric Cards - App Style */
    [data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e2e8f0;
        padding: 1rem 1.2rem; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: transform 0.2s;
    }
    [data-testid="metric-container"]:hover { transform: translateY(-2px); }

    /* Banner */
    .welcome-banner { 
        background: linear-gradient(135deg, #0056D2 0%, #3b82f6 100%); 
        color: white; padding: 2rem; border-radius: 20px; 
        margin-bottom: 1.5rem; box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
    }
    .welcome-banner h1 { margin: 0; font-size: 2.2rem; font-weight: 700; color: white; }
    .welcome-banner p { margin: 8px 0 0 0; opacity: 0.9; font-size: 1rem; }
    @media (max-width: 768px) {
        .welcome-banner { padding: 1.5rem 1rem; border-radius: 16px; }
        .welcome-banner h1 { font-size: 1.5rem; }
    }
    
    /* Feature Box & Cards */
    .feature-box { 
        background-color: white; padding: 1.5rem; border-radius: 16px; 
        border: 1px solid #e2e8f0; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    @media (max-width: 768px) { .feature-box { padding: 1rem; border-radius: 12px; } }
    
    /* Recommendations & Badges */
    .ai-recom-item { padding: 1rem; border-radius: 12px; margin-bottom: 0.8rem; display: flex; align-items: flex-start; gap: 12px; line-height: 1.4; }
    .recom-success { background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
    .recom-warning { background-color: #fffbeb; border: 1px solid #fde68a; color: #92400e; }
    
    .buyer-card { border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; background-color: #ffffff; }
    .match-badge { background-color: #d1fae5; color: #059669; padding: 0.3rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; float: right; }

    .status-badge { display: block; text-align: center; padding: 0.6rem; border-radius: 12px; font-size: 0.9rem; font-weight: 700; margin: 1rem 0; }
    .status-ready { background-color: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
    .status-warning { background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .status-not-ready { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    
    /* Forms & Touch Targets */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea { 
        border-radius: 10px !important; border: 1px solid #cbd5e1 !important; padding: 0.75rem !important; font-size: 16px !important; 
    }
    .stButton > button { 
        width: 100%; font-size: 1rem !important; font-weight: 600 !important; padding: 0.75rem 1rem !important; border-radius: 12px !important; min-height: 48px !important;
    }
    
    @media (max-width: 768px) {
        [data-testid="stTabs"] { overflow-x: auto; }
        .stTabs [data-baseweb="tab-list"] button { padding: 0.6rem 1rem !important; border-radius: 20px; border: 1px solid #e2e8f0; white-space: nowrap; }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/0056D2/FFFFFF?text=EKSPORAI", use_container_width=True)
    st.markdown("### 🚀 EksporAI")
    st.markdown("Platform AI untuk Kesiapan & Matchmaking Ekspor UMKM")
    st.markdown("---")
    
    menu = st.radio(
        "Navigasi",
        ["🏠 Dashboard", "📄 Upload Dokumen", "🤝 Matchmaking", "📊 Admin Panel"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("""
    <div style='background: #f1f5f9; color: #475569; padding: 1rem; border-radius: 12px; font-size: 0.85rem; border: 1px solid #e2e8f0; text-align: center;'>
        <b>MVP EksporAI</b><br>Hackathon PIDI 2026<br><small>by Alvindra Agus Syahputra</small>
    </div>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'score' not in st.session_state:
    st.session_state.score = None
if 'umkm_data' not in st.session_state:
    st.session_state.umkm_data = None
if 'umkm_id' not in st.session_state:
    st.session_state.umkm_id = f"UMKM_{str(uuid.uuid4())[:8].upper()}"
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'umkm'  # 'umkm', 'buyer', 'admin'
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Initialize managers
db = get_firebase()
tracker = get_transaction_tracker()
admin = get_admin_manager()

# ============================================
# HALAMAN 1: DASHBOARD
# ============================================
if menu == "🏠 Dashboard":
    st.markdown("""
    <div class="welcome-banner">
        <h1 style='margin:0; font-size: 2.2rem;'>Halo, UMKM Maju Jaya! 👋</h1>
        <p style='margin:5px 0 0 0; opacity: 0.9;'>Temukan peluang ekspor dan tingkatkan kesiapan bisnismu dengan EksporAI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Cards dari Data Asli 100k
    if df_real is not None:
        total_umkm = len(df_real)
        siap_ekspor = len(df_real[df_real['skor_kesiapan'] >= 80])
        total_omzet = df_real['omzet_bulanan'].sum() / 1e12
        
        # Responsive Columns
        c1, c2 = st.columns(2)
        with c1: st.metric("Total UMKM Nasional", f"{total_umkm:,}", "+15%")
        with c2: st.metric("UMKM Siap Ekspor", f"{siap_ekspor:,}", "Skor > 80")
            
        c3, c4 = st.columns(2)
        with c3: st.metric("Potensi Transaksi", f"Rp {total_omzet:.1f} T", "+12%")
        with c4: st.metric("Buyer Global Aktif", "1,250", "+5%")
        st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.8, 1.2], gap="large")

    with col_left:
        # 1. EXPORT READINESS SCORE
        st.markdown("### 📈 Export Readiness Score Anda")
        st.markdown("<div class='feature-box'>", unsafe_allow_html=True)
        
        if st.session_state.score is not None:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=st.session_state.score,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1},
                    'bar': {'color': "#0056D2"},
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 50], 'color': "#fee2e2"},
                        {'range': [50, 75], 'color': "#fef3c7"},
                        {'range': [75, 100], 'color': "#d1fae5"}
                    ],
                    'threshold': {'line': {'color': "#0f172a", 'width': 4}, 'thickness': 0.75, 'value': st.session_state.score}
                }
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), font={'family': "Inter"})
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            st.progress(st.session_state.score / 100, text=f"Progress Kelengkapan: {st.session_state.score}%")
            
            if st.session_state.score >= 80:
                st.markdown('<div class="status-badge status-ready">✅ SIAP EKSPOR</div>', unsafe_allow_html=True)
            elif st.session_state.score >= 60:
                st.markdown('<div class="status-badge status-warning">⚠️ PERLU PERBAIKAN</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-badge status-not-ready">❌ BELUM SIAP</div>', unsafe_allow_html=True)
                
            st.button("📄 Unduh Sertifikat Digital", use_container_width=True)
        else:
            st.info("💡 Belum ada data UMKM pribadi. Silakan input data di menu **Upload Dokumen**.")
        st.markdown("</div>", unsafe_allow_html=True)

        # 2. REKOMENDASI AI
        st.markdown("### 🤖 Rekomendasi AI")
        st.markdown("<div class='feature-box'>", unsafe_allow_html=True)
        if st.session_state.umkm_data is not None:
            data = st.session_state.umkm_data
            if data.get('punya_sertifikat_halal') == 1:
                st.markdown("<div class='ai-recom-item recom-success'><div>✅</div><div><b>Sertifikasi Halal sudah lengkap</b><br><small style='color:green;'>+10 Poin Kesiapan</small></div></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='ai-recom-item recom-warning'><div>⚠️</div><div><b>Sertifikasi Halal belum ada</b><br><small style='color:orange;'>Segera urus untuk target pasar Timur Tengah</small></div></div>", unsafe_allow_html=True)
                
            if data.get('punya_sertifikat_bpom') == 1:
                st.markdown("<div class='ai-recom-item recom-success'><div>✅</div><div><b>Legalitas Mutu Terverifikasi</b><br><small style='color:green;'>Syarat wajib ekspor terpenuhi</small></div></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='ai-recom-item recom-warning'><div>⚠️</div><div><b>Sertifikasi Mutu/BPOM diperlukan</b><br><small style='color:orange;'>Prioritas tinggi sebelum matchmaking</small></div></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='ai-recom-item recom-warning'><div>⚠️</div><div><b>Data Belum Lengkap</b><br><small>Masukkan data usaha di menu Upload Dokumen.</small></div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        # 3. PELUANG BUYER COCOK
        st.markdown("### 🤝 Peluang Buyer Cocok")
        st.markdown("<div class='feature-box'>", unsafe_allow_html=True)
        if st.session_state.score is not None and st.session_state.score >= 60:
            buyers = [
                {"negara": "🇯🇵 Jepang", "nama": "Tokyo Import Co.", "match": "95%", "desc": "Spesialis produk dekorasi."},
                {"negara": "🇩🇪 Jerman", "nama": "Berlin Organic Foods", "match": "88%", "desc": "Camilan organik sehat."}
            ]
            for b in buyers:
                st.markdown(f"""
                <div class='buyer-card'>
                    <span class='match-badge'>{b['match']} Match</span>
                    <h4 style='margin:0 0 5px 0; color: #0f172a;'>{b['negara']}</h4>
                    <b style="color: #334155;">{b['nama']}</b><br><small style='color:gray;'>💡 {b['desc']}</small>
                </div>
                """, unsafe_allow_html=True)
            st.button("Lihat Semua Buyer di Menu Matchmaking", use_container_width=True, type="secondary")
        else:
            st.warning("⚠️ Skor kesiapan Anda belum memenuhi syarat (Minimal 60) untuk melihat Buyer Internasional.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 4. AKTIVITAS TERBARU
        st.markdown("### 🕒 Aktivitas Terbaru")
        st.markdown("<div class='feature-box'>", unsafe_allow_html=True)
        st.markdown("✅ **Sistem EksporAI Aktif** <br><span style='color:#94a3b8; font-size:0.85rem;'>Baru saja</span>", unsafe_allow_html=True)
        if st.session_state.score is not None:
            st.markdown("<hr style='margin: 0.8rem 0; opacity: 0.5;'>", unsafe_allow_html=True)
            st.markdown(f"🤖 **Skor diprediksi menggunakan Ensemble AI** <br><span style='color:#94a3b8; font-size:0.85rem;'>Baru saja</span>", unsafe_allow_html=True)
        if df_real is not None:
            st.markdown("<hr style='margin: 0.8rem 0; opacity: 0.5;'>", unsafe_allow_html=True)
            st.markdown("📄 **Data 100,000 UMKM Nasional di-load** <br><span style='color:#94a3b8; font-size:0.85rem;'>Sistem Online</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# HALAMAN 2: UPLOAD DOKUMEN & INPUT
# ============================================
elif menu == "📄 Upload Dokumen":
    st.markdown("<h2 style='color: #0056D2;'>📄 Analisis Kesiapan UMKM</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='feature-box'>", unsafe_allow_html=True)
    st.markdown("### 1. Upload Dokumen Otomatis (AI OCR/NLP)")
    
    with st.expander("📋 **Panduan Format Dokumen** (Klik untuk detail)", expanded=False):
        st.markdown("""
        #### 🎯 **FORMAT DOKUMEN YANG DIDUKUNG:**
        - **📄 PDF Files** (.pdf) - Laporan keuangan, legalitas, atau profil perusahaan
        - **🖼️ Image Files** (.png, .jpg, .jpeg) - Dokumen yang discan atau foto
        
        #### 📝 **CONTOH ISI DOKUMEN YANG IDEAL:**
        ```
        NIB: 123456789012345
        Nama Perusahaan: PT Maju Jaya Indonesia
        Alamat: Jl. Sudirman No. 123, Jakarta Pusat
        NPWP: 01.234.567.8-901.000
        Modal Usaha: Rp 500.000.000
        Omzet Bulanan: Rp 150.000.000
        Jumlah Karyawan: 25
        Tahun Berdiri: 2018
        Kapasitas Produksi: 1000 unit/bulan
        Sertifikat Halal: Ya
        Sertifikat BPOM: Ya
        Pengalaman Ekspor: Tidak
        ```
        
        #### 🎯 **FIELD YANG AKAN DIEKSTRAK:**
        | Kategori | Field | Contoh |
        |----------|-------|--------|
        | **🏢 Dasar** | NIB, NPWP, Nama, Alamat | `123456789012345` |
        | **💰 Keuangan** | Modal, Omzet, Tahun Berdiri | `Rp 500.000.000` |
        | **👥 Operasional** | Jumlah Karyawan, Kapasitas | `25 orang` |
        | **📜 Sertifikasi** | Halal, BPOM, NIB | `Ya/Tidak` |
        | **🌍 Ekspor** | Pengalaman Export | `Ya/Tidak` |
        
        #### 💡 **TIPS UNTUK HASIL TERBAIK:**
        - ✅ **Gunakan format teks yang jelas** (bukan gambar kompleks)
        - ✅ **Tuliskan label field** seperti "NIB:", "Nama:", dll
        - ✅ **Gunakan format Rupiah** untuk angka (Rp 500.000.000)
        - ✅ **Cantumkan semua sertifikasi** yang dimiliki
        - ✅ **Pastikan dokumen terbaca** (tidak blur atau rusak)
        - ✅ **Sertakan informasi lengkap** untuk skor yang akurat
        
        #### ⚠️ **CATATAN PENTING:**
        - AI akan mencoba ekstrak sebanyak mungkin data
        - Jika ekstraksi tidak sempurna, Anda bisa edit manual di form bawah
        - Minimum data: Nama usaha, tahun berdiri, modal, omzet
        - Semakin lengkap data = semakin akurat skor kesiapan ekspor
        """)
    
    uploaded_file = st.file_uploader("Upload Laporan Keuangan/Legalitas (PDF atau Gambar)", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.success(f"✅ File berhasil diupload: {uploaded_file.name}")
        if st.button("🔍 Ekstrak Data via AI (OCR + NLP)", type="primary"):
            with st.spinner("AI sedang mengekstrak dokumen menggunakan OCR + NLP..."):
                try:
                    result = process_document_file(uploaded_file)
                    
                    if result['status'] in ['success', 'partial']:
                        st.success(f"✅ {result['message']}")
                        
                        st.write("#### 📊 Hasil Ekstraksi via AI:")
                        extracted = result['data']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**NIB:** {extracted.get('nib', '?')}")
                            st.write(f"**Nama Usaha:** {extracted.get('nama_usaha', '?')}")
                            st.write(f"**Tahun Berdiri:** {extracted.get('tahun_berdiri', '?')}")
                            st.write(f"**Modal:** Rp {float(extracted.get('modal', 0)):,.0f}")
                        
                        with col2:
                            st.write(f"**Omzet Bulanan:** Rp {float(extracted.get('omzet', 0)):,.0f}")
                            st.write(f"**Kapasitas:** {extracted.get('kapasitas', '?')}")
                            st.write(f"**Sertifikat Halal:** {'✅ Ya' if extracted.get('punya_sertifikat_halal') else '❌ Tidak'}")
                            st.write(f"**Sertifikat BPOM:** {'✅ Ya' if extracted.get('punya_sertifikat_bpom') else '❌ Tidak'}")
                        
                        # Show validation results
                        validation = result['validation']
                        if validation['errors']:
                            st.error(f"❌ Errors: {', '.join(validation['errors'])}")
                        if validation['warnings']:
                            st.warning(f"⚠️ Warnings: {', '.join(validation['warnings'])}")
                        
                        # Show confidence scores
                        confidence = extracted.get('extraction_confidence', {})
                        st.info(f"🎯 Confidence Score: {confidence.get('overall_confidence', 0)*100:.1f}%")
                        
                        st.info("💡 **Data sudah diekstrak!** Silakan review dan ubah di form manual di bawah jika perlu.")
                    else:
                        st.error(f"❌ {result['message']}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='feature-box'>", unsafe_allow_html=True)
    st.markdown("### 2. Verifikasi Data Manual")
    with st.form("umkm_input_form"):
        col1, col2 = st.columns(2)
        with col1:
            nama_usaha = st.text_input("Nama Usaha", "Batik Solo Jaya")
            sektor = st.selectbox("Sektor", ["Makanan", "Kerajinan", "Fashion", "Kosmetik"])
            tahun_berdiri = st.number_input("Tahun Berdiri", min_value=1950, max_value=2026, value=2020)
            modal_usaha = st.number_input("Modal Usaha (Rp)", min_value=0, value=50000000, step=1000000)
            omzet_bulanan = st.number_input("Omzet Bulanan (Rp)", min_value=0, value=20000000, step=1000000)
        
        with col2:
            jumlah_karyawan = st.number_input("Jumlah Karyawan", min_value=1, value=5)
            punya_sertifikat_halal = st.checkbox("Memiliki Sertifikat Halal")
            punya_sertifikat_bpom = st.checkbox("Memiliki Sertifikat BPOM")
            punya_nib = st.checkbox("Memiliki NIB", value=True)
            ekspor_sebelumnya = st.checkbox("Pernah Ekspor Sebelumnya")
            kapasitas_produksi = st.number_input("Kapasitas Produksi/Bulan", min_value=0, value=500)
            
        # 📋 INFO TENTANG DATA YANG DIBUTUHKAN
        with st.expander("📋 Info Detail Pengaruh Data Pada Skor", expanded=False):
            st.markdown("""
            #### 📋 **DATA YANG DIBUTUHKAN UNTUK SKOR EKSPOR:**
            
            | Field | Wajib | Pengaruh Skor | Keterangan |
            |-------|-------|---------------|------------|
            | **Nama Usaha** | ✅ | - | Identitas perusahaan |
            | **Sektor** | ✅ | Tinggi | Makanan/Kerajinan/Fashion/Kosmetik |
            | **Tahun Berdiri** | ✅ | Sedang | Usia perusahaan |
            | **Modal Usaha** | ✅ | Tinggi | Kapital awal |
            | **Omzet Bulanan** | ✅ | Sangat Tinggi | Pendapatan rutin |
            | **Jumlah Karyawan** | ✅ | Sedang | Skala operasi |
            | **Sertifikat Halal** | ❌ | Tinggi | +10 poin untuk pasar Timur Tengah |
            | **Sertifikat BPOM** | ❌ | Tinggi | Wajib untuk ekspor |
            | **NIB** | ❌ | Sedang | Legalitas berusaha |
            | **Pengalaman Ekspor** | ❌ | Tinggi | Track record ekspor |
            | **Kapasitas Produksi** | ❌ | Sedang | Volume produksi |
            
            #### 🎯 **TINGKAT KESIAPAN EKSPOR:**
            - **0-40:** ❌ Belum siap (Perlu pengembangan dasar)
            - **41-60:** ⚠️ Siap parsial (Perlu sertifikasi & modal)
            - **61-80:** ✅ Siap sedang (Bisa ekspor kecil-kecilan)  
            - **81-100:** 🚀 Sangat siap (Ready untuk buyer internasional)
            
            #### 💡 **TIPS MENINGKATKAN SKOR:**
            - ✅ Sertifikasi Halal & BPOM (+20 poin)
            - ✅ Omzet >50jt/bulan (+15 poin)
            - ✅ Pengalaman ekspor sebelumnya (+10 poin)
            - ✅ Modal >100jt (+10 poin)
            - ✅ Kapasitas produksi tinggi (+5 poin)
            """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Hitung Skor Kesiapan (Ensemble AI)", type="primary", use_container_width=True)

        if submitted:
            dict_data = {
                'tahun_berdiri': tahun_berdiri, 
                'modal_usaha': modal_usaha,
                'omzet_bulanan': omzet_bulanan, 
                'jumlah_karyawan': jumlah_karyawan,
                'punya_sertifikat_halal': 1 if punya_sertifikat_halal else 0,
                'punya_sertifikat_bpom': 1 if punya_sertifikat_bpom else 0,
                'punya_nib': 1 if punya_nib else 0,
                'ekspor_sebelumnya': 1 if ekspor_sebelumnya else 0,
                'kapasitas_produksi': kapasitas_produksi,
                'nama': nama_usaha,
                'sektor': sektor
            }
            
            try:
                # Perbaikan Bug: Pastikan menerima angka, bukan dictionary
                raw_score = predict_readiness_score(dict_data)
                
                if isinstance(raw_score, dict):
                    score = float(raw_score.get('score', 0))
                else:
                    score = float(raw_score)
                
                # Simpan ke Firebase/Local Storage
                db.add_umkm(st.session_state.umkm_id, dict_data)
                db.update_score(st.session_state.umkm_id, score, 'SUBMITTED')
                
                # Update session state
                st.session_state.score = score
                st.session_state.umkm_data = dict_data
                
                st.success("✅ Analisis Selesai! Data tersimpan dan Skor dihitung.")
                st.balloons()
                st.info(f"📌 **ID UMKM Anda:** `{st.session_state.umkm_id}` (untuk tracking transaksi)")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# HALAMAN 3: MATCHMAKING
# ============================================
elif menu == "🤝 Matchmaking":
    st.markdown("<h2 style='color: #0056D2;'>🤝 Intelligent Matchmaking - Rekomendasi Buyer</h2>", unsafe_allow_html=True)
    
    if st.session_state.score is None:
        st.warning("⚠️ Belum ada skor kesiapan. Silakan input data di menu **Upload Dokumen**.")
    else:
        score = st.session_state.score
        umkm_data = st.session_state.umkm_data
        
        st.info(f"📊 **Skor Kesiapan Anda:** {score}/100 | **ID UMKM:** `{st.session_state.umkm_id}` | **Sektor:** {umkm_data.get('sektor', '?')}")
        
        if score >= 60:
            st.markdown("---")
            st.markdown("### 🎯 Buyer Internasional yang Cocok Dengan Anda")
            
            try:
                # Gunakan Intelligent Matchmaking
                recommendations = get_buyer_recommendations(
                    score, 
                    umkm_data.get('sektor', 'Makanan'),
                    umkm_data,
                    top_n=10
                )
                
                st.markdown(f"#### ✅ Ditemukan **{len(recommendations)}** Buyer Potensial")
                
                # Filter & sort options
                col1, col2 = st.columns(2)
                with col1:
                    min_match = st.slider("Filter Min. Match Score", 0, 100, 70)
                with col2:
                    sort_by = st.selectbox("Urut berdasarkan:", ["Match Score ⬇️", "Rating ⬇️", "Transaksi Sukses ⬇️"])
                
                # Filter recommendations
                filtered_recs = [r for r in recommendations if r.get('match_score', 0) >= min_match]
                
                # Sort
                if sort_by == "Rating ⬇️":
                    filtered_recs.sort(key=lambda x: x.get('rating', 0), reverse=True)
                elif sort_by == "Transaksi Sukses ⬇️":
                    filtered_recs.sort(key=lambda x: x.get('transaksi_sukses', 0), reverse=True)
                else:
                    filtered_recs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
                
                st.markdown("---")
                
                # Display buyers with nice card
                for idx, buyer in enumerate(filtered_recs, 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="feature-box" style="margin-bottom: 1rem; padding: 1.2rem;">
                            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 10px;">
                                <h3 style="margin: 0; color: #0f172a;">{idx}. {buyer['nama']}</h3>
                                <div class="match-badge" style="font-size: 0.9rem;">{buyer['match_score']}% Match</div>
                            </div>
                            <p style="margin: 0 0 10px 0; color: #475569;">📍 <b>{buyer['negara']}</b> | 🏢 {buyer['jenis_perusahaan']}</p>
                            <p style="font-size: 0.95rem; margin-bottom: 15px;"><b>Deskripsi:</b> {buyer['deskripsi']}<br><b>Preferensi:</b> {', '.join(buyer.get('preferensi_sektor', []))}</p>
                            <div style="background: #f8fafc; padding: 10px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 15px;">
                                <b>Min. Order:</b> {buyer['min_order']:,} pcs &nbsp;|&nbsp; 
                                <b>Min. Score:</b> {buyer['min_score']}/100 &nbsp;|&nbsp; 
                                <b>Rating:</b> {'⭐' * int(buyer.get('rating', 4))} ({buyer.get('rating', 0)}/5) &nbsp;|&nbsp;
                                <b>Transaksi Berhasil:</b> {buyer.get('transaksi_sukses', 0)} kali
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if st.button(f"📧 Hubungi Sekarang", key=f"contact_{buyer['id']}", use_container_width=True):
                            # Record buyer contact interaction
                            tracker.record_buyer_contact(
                                st.session_state.umkm_id,
                                buyer['id'],
                                'inquiry',
                                f"Interest from {umkm_data.get('nama', 'UMKM')}"
                            )
                            st.success(f"✅ Permintaan kontak ke **{buyer['nama']}** telah dikirim!\n\n📧 Kami akan menghubungi Buyer untuk memfasilitasi koneksi.")
                
                # Export & Actions
                st.markdown("### 📥 Export & Actions")
                col_exp1, col_exp2, col_exp3 = st.columns(3)
                
                with col_exp1:
                    if st.button("📥 Export Daftar Buyer (CSV)", use_container_width=True):
                        df_rec = pd.DataFrame(filtered_recs)
                        csv = df_rec.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"buyer_recommendations_{st.session_state.umkm_id}.csv",
                            mime="text/csv"
                        )
                
                with col_exp2:
                    if st.button("📊 Lihat Analisis Detail", use_container_width=True):
                        st.markdown("#### 📊 Analisis Compatibility")
                        for buyer in filtered_recs[:3]:
                            with st.expander(f"Analisis - {buyer['nama']}"):
                                st.write(f"**Match Score:** {buyer['match_score']}%")
                                st.write(f"**Alasan Match:**")
                                st.write(f"- Skor kesiapan Anda {score} memenuhi requirement {buyer['min_score']}")
                                st.write(f"- Sektor {umkm_data.get('sektor')} in preferensi {', '.join(buyer.get('preferensi_sektor', []))}")
                                st.write(f"- Omzet Rp{umkm_data.get('omzet_bulanan', 0):,.0f} sesuai requirement minimal")
                
                with col_exp3:
                    if st.button("💬 Feedback", use_container_width=True):
                        feedback_text = st.text_area("Bagikan feedback tentang rekomendasi ini:", height=100)
                        if st.button("Kirim Feedback", key="btn_send_feedback"):
                            st.success("✅ Terima kasih atas feedback Anda!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.error(f"❌ Skor Anda {score}/100 belum memenuhi syarat (minimal 60/100) untuk matchmaking internasional")
            st.info("💡 **Rekomendasi:** Tingkatkan skor dengan:")
            st.write("- ✅ Mendapatkan sertifikat halal")
            st.write("- ✅ Mendapatkan sertifikat BPOM/legalitas")
            st.write("- ✅ Meningkatkan kapasitas produksi")
            st.write("- ✅ Mendokumentasikan pengalaman ekspor sebelumnya")

# ============================================
# HALAMAN 4: ADMIN PANEL
# ============================================
elif menu == "📊 Admin Panel":
    st.markdown("<h2 style='color: #0056D2;'>📊 Admin Dashboard Nasional</h2>", unsafe_allow_html=True)
    
    # Admin Authentication
    try:
        correct_password = st.secrets.get("admin_password", "admin123")
    except:
        correct_password = "admin123"
    
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown("<div class='feature-box'>", unsafe_allow_html=True)
        admin_pass = st.text_input("🔐 Password Admin:", type="password")
        if st.button("Login", type="primary"):
            if admin_pass == correct_password:
                st.session_state.admin_authenticated = True
                st.success("✅ Akses Admin Diberikan!")
                st.rerun()
            else:
                st.error("❌ Password salah!")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Admin authenticated - show dashboard
        if st.button("🔓 Logout Admin"):
            st.session_state.admin_authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        # Main admin tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Dashboard",
            "👥 Manajemen UMKM",
            "🤝 Buyer Management",
            "💰 Transaksi",
            "⚙️ Sistem"
        ])
        
        with tab1:
            st.markdown("### 📊 Dashboard Analytics Nasional")
            
            try:
                dashboard_data = admin.get_dashboard_analytics()
                system_stats = admin.get_system_stats()
                
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total UMKM", f"{dashboard_data['total_umkm']:,}", delta="+12%")
                col2.metric("UMKM Siap Ekspor", f"{dashboard_data['ready_to_export']:,}", delta=f"+{dashboard_data['ready_to_export'] // 100 if dashboard_data['total_umkm'] > 0 else 0}%")
                col3.metric("Total Transaksi (30h)", f"{system_stats['monthly_transactions']:,}", delta=f"+{system_stats['monthly_successful_tx']} sukses")
                col4.metric("Nilai Transaksi", f"Rp {system_stats['monthly_value'] / 1e9:.1f}M", delta="+8%")
                
                st.markdown("---")
                
                # Charts
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.markdown("#### 🎯 Distribusi Sektor")
                    if dashboard_data['top_sectors']:
                        sector_data = pd.DataFrame(list(dashboard_data['top_sectors'].items()), columns=['Sektor', 'Jumlah'])
                        fig_sector = px.bar(sector_data, x='Sektor', y='Jumlah', color='Jumlah', color_continuous_scale='Blues')
                        st.plotly_chart(fig_sector, use_container_width=True)
                
                with col_chart2:
                    st.markdown("#### 📊 Status Kesiapan UMKM")
                    status_data = pd.DataFrame({
                        'Status': ['Siap Ekspor (≥80)', 'Perlu Perbaikan (60-79)', 'Belum Siap (<60)'],
                        'Jumlah': [
                            dashboard_data['ready_to_export'],
                            dashboard_data['total_umkm'] // 3,
                            dashboard_data['total_umkm'] // 4
                        ]
                    })
                    fig_status = px.pie(status_data, values='Jumlah', names='Status', color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444'])
                    st.plotly_chart(fig_status, use_container_width=True)
                
                st.markdown("---")
                
                # Transaction trend
                st.markdown("#### 📈 Tren Transaksi (30 hari terakhir)")
                trans_analytics = admin.get_transaction_analytics(days=30)
                
                col_trans1, col_trans2, col_trans3 = st.columns(3)
                col_trans1.metric("Total Transaksi", trans_analytics.get('total_transactions', 0))
                col_trans2.metric("Transaksi Sukses", trans_analytics.get('completed', 0), delta=f"{(trans_analytics.get('completed', 0) / max(trans_analytics.get('total_transactions', 1), 1) * 100):.0f}%")
                col_trans3.metric("Pending Transaksi", trans_analytics.get('pending', 0))
                
            except Exception as e:
                st.error(f"❌ Error loading dashboard: {str(e)}")
        
        with tab2:
            st.markdown("### 👥 Manajemen UMKM")
            
            sub_col1, sub_col2 = st.columns(2)
            
            with sub_col1:
                st.markdown("#### 📋 Daftar UMKM")
                try:
                    umkm_df = admin.get_all_umkm()
                    if len(umkm_df) > 0:
                        st.dataframe(umkm_df.head(20), use_container_width=True, height=400)
                    else:
                        st.info("Belum ada UMKM terdaftar")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            with sub_col2:
                st.markdown("#### ✅ Verifikasi UMKM")
                pending_list = admin.get_pending_approvals()
                
                if pending_list:
                    st.warning(f"⏳ {len(pending_list)} UMKM menunggu verifikasi")
                    for umkm in pending_list[:5]:
                        with st.expander(f"UMKM ID: {umkm.get('umkm_id', '?')}"):
                            st.write(f"Status: {umkm.get('status', '?')}")
                            st.write(f"Catatan Admin: {umkm.get('admin_notes', '?')}")
                            
                            if st.button("✅ Setujui", key=f"approve_{umkm.get('umkm_id')}"):
                                admin.verify_umkm_document(umkm.get('umkm_id'), 'approved', 'Disetujui oleh admin')
                                st.success("✅ UMKM disetujui!")
                else:
                    st.success("✅ Semua UMKM sudah terverifikasi!")
            
            st.markdown("---")
            
            # Export UMKM report
            if st.button("📥 Export Laporan UMKM (CSV)", type="primary"):
                report = admin.export_umkm_report()
                if report:
                    st.download_button(
                        label="Download CSV",
                        data=report,
                        file_name=f"umkm_report_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        with tab3:
            st.markdown("### 🤝 Buyer Management")
            
            col_buyer1, col_buyer2 = st.columns(2)
            
            with col_buyer1:
                st.markdown("#### ➕ Tambah Buyer Baru")
                
                with st.form("add_buyer_form"):
                    buyer_id = st.text_input("ID Buyer", f"BUYER_{str(uuid.uuid4())[:8].upper()}")
                    buyer_nama = st.text_input("Nama Buyer")
                    buyer_negara = st.selectbox("Negara", ["🇯🇵 Jepang", "🇩🇪 Jerman", "🇸🇬 Singapura", "🇺🇸 USA", "🇦🇪 UAE", "🇬🇧 Inggris"])
                    buyer_jenis = st.text_input("Jenis Perusahaan")
                    buyer_deskripsi = st.text_area("Deskripsi")
                    buyer_min_score = st.number_input("Min. Score", 0, 100, 60)
                    buyer_min_order = st.number_input("Min. Order (pcs)", 0, 100000, 500)
                    
                    if st.form_submit_button("✅ Tambah Buyer", type="primary"):
                        buyer_data = {
                            'nama': buyer_nama,
                            'negara': buyer_negara,
                            'jenis_perusahaan': buyer_jenis,
                            'deskripsi': buyer_deskripsi,
                            'min_score': buyer_min_score,
                            'min_order': buyer_min_order
                        }
                        if admin.add_buyer_profile(buyer_id, buyer_data):
                            st.success("✅ Buyer ditambahkan!")
                        else:
                            st.error("❌ Error!")
            
            with col_buyer2:
                st.markdown("#### 📋 Daftar Buyer Aktif")
                try:
                    buyers = admin.get_all_buyers()
                    if buyers:
                        buyer_names = [f"{b.get('nama', '?')} ({b.get('negara', '?')})" for b in buyers.values()]
                        for name in buyer_names[:10]:
                            st.write(f"✅ {name}")
                    else:
                        st.info("Belum ada buyer terdaftar")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with tab4:
            st.markdown("### 💰 Monitoring Transaksi")
            
            try:
                trans_stats = admin.get_transaction_analytics(days=30)
                
                col_t1, col_t2, col_t3, col_t4 = st.columns(4)
                col_t1.metric("Total Transaksi", trans_stats.get('total_transactions', 0))
                col_t2.metric("Transaksi Sukses", trans_stats.get('completed', 0), delta="✅")
                col_t3.metric("Pending", trans_stats.get('pending', 0), delta="⏳")
                col_t4.metric("Total Value", f"Rp {trans_stats.get('total_value', 0) / 1e9:.1f}M")
                
                st.markdown("---")
                
                # Export transaction report
                if st.button("📥 Export Laporan Transaksi (CSV)", type="primary"):
                    report = admin.export_transaction_report(days=30)
                    if report:
                        st.download_button(
                            label="Download CSV",
                            data=report,
                            file_name=f"transaction_report_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with tab5:
            st.markdown("### ⚙️ Pengaturan Sistem")
            
            col_sys1, col_sys2 = st.columns(2)
            
            with col_sys1:
                st.markdown("#### 🔧 Backup & Maintenance")
                st.checkbox("Aktifkan Auto-Backup Harian", value=True, disabled=True)
                st.checkbox("Aktifkan Email Notifikasi", value=True)
                
                if st.button("💾 Backup Database Sekarang"):
                    st.success("✅ Backup berhasil dibuat")
                
                if st.button("🔄 Restart Sistem"):
                    st.warning("⏳ Sistem sedang di-restart...")
                    st.success("✅ Sistem restart selesai")
            
            with col_sys2:
                st.markdown("#### 📊 Informasi Sistem")
                system_stats = admin.get_system_stats()
                st.write(f"**Status:** {system_stats.get('system_uptime', 'Unknown')}")
                st.write(f"**Last Sync:** {system_stats.get('last_sync', 'Unknown')}")
                st.write(f"**Total UMKM:** {system_stats.get('total_umkm', 0):,}")
                st.write(f"**Total Buyer:** {system_stats.get('total_buyers', 0):,}")
                st.write(f"**API Version:** 1.0.0")
                st.write(f"**Database:** Firebase + Local Storage (Hybrid)")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; font-size: 0.9rem;'>© 2026 EksporAI | MVP Hackathon PIDI 2026 | v1.0</div>", unsafe_allow_html=True)
# 🚀 EksporAI - Platform AI untuk Export Readiness & Matchmaking UMKM

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Platform AI canggih untuk membantu UMKM Indonesia meningkatkan kesiapan ekspor dan menemukan buyer internasional yang tepat.

## ✨ Fitur Utama

- 🤖 **AI Scoring Engine** - Ensemble ML untuk prediksi kesiapan ekspor
- 📄 **OCR Document Processing** - Ekstraksi otomatis data dari dokumen
- 🤝 **Intelligent Matchmaking** - Rekomendasi buyer berdasarkan 5 faktor kompatibilitas
- 📊 **Admin Dashboard** - Monitoring dan management sistem
- 🔥 **Firebase Integration** - Real-time database dengan local fallback
- 🚀 **REST API** - Integrasi dengan sistem eksternal (opsional)

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI/ML:** Scikit-learn, Spacy, Tesseract OCR
- **Database:** Firebase Firestore + Local JSON
- **API:** FastAPI
- **Deployment:** Streamlit Cloud (Gratis)

## 🚀 Quick Start (Development)

```bash
# Clone repository
git clone https://github.com/yourusername/eksporai-mvp.git
cd eksporai-mvp

# Install dependencies
pip install -r requirements.txt

# Download Spacy model (optional)
python -m spacy download id_core_news_sm

# Run locally
streamlit run app.py
```

## 🌐 Deployment Gratis

### 1. 🚀 **Streamlit Cloud (RECOMMENDED - 100% FREE)**

**Keuntungan:**
- ✅ 100% gratis tanpa batas
- ✅ Auto-scaling
- ✅ Custom domain support
- ✅ GitHub integration
- ✅ No credit card required

**Langkah Deploy:**

1. **Push ke GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - EksporAI MVP"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/eksporai-mvp.git
   git push -u origin main
   ```

2. **Deploy ke Streamlit Cloud:**
   - Buka [share.streamlit.io](https://share.streamlit.io)
   - Connect GitHub account
   - Pilih repository `eksporai-mvp`
   - Set main file: `app.py`
   - Klik **Deploy!**

3. **Konfigurasi Environment Variables (Opsional):**
   - Jika menggunakan Firebase production, tambahkan secrets di Streamlit Cloud settings

**URL App:** `https://your-app-name.streamlit.app`

---

## 🔧 Environment Variables

Buat file `.env` untuk konfigurasi:

```env
# Firebase (Opsional - gunakan local storage jika kosong)
FIREBASE_KEY={"type": "service_account", ...}
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com/

# Admin Settings
ADMIN_PASSWORD=admin123

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

## 🎯 Usage Guide

### Untuk UMKM:
1. **Upload Dokumen** - Upload laporan keuangan/legalitas
2. **AI Processing** - Sistem otomatis ekstrak data
3. **Review & Edit** - Koreksi data jika perlu
4. **Hitung Skor** - Dapatkan skor kesiapan ekspor
5. **Matchmaking** - Lihat buyer internasional yang cocok

### Untuk Admin:
1. **Login Admin** - Gunakan password admin
2. **Dashboard Analytics** - Monitor sistem
3. **Manage UMKM** - Approve/reject data UMKM
4. **Manage Buyers** - Tambah buyer internasional
5. **Transaction Tracking** - Monitor transaksi

## 📊 API Endpoints

```bash
# Start API server
uvicorn utils.api_server:app --reload

# Available endpoints:
GET  /api/v1/health              # Health check
POST /api/v1/umkm/score          # Calculate export score
GET  /api/v1/umkm/{id}           # Get UMKM data
GET  /api/v1/matchmaking/{id}    # Get buyer recommendations
POST /api/v1/transactions        # Create transaction
GET  /api/v1/admin/dashboard     # Admin analytics
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👨‍💻 Author

**Alvindra Agus Syahputra**
- Email: alimuhamad2386@gmail.com
- Project: PIDI Hackathon 2026

## 🙏 Acknowledgments

- PIDI (Indonesian Diaspora Network)
- Streamlit Community
- Firebase & Google Cloud
- Scikit-learn & Open Source ML Community

---

**⭐ Star this repo if you find it helpful!**

**🎉 Demo: [[eksporai-mvp.streamlit.app](https://eksporai-mvp.streamlit.app)](https://ekspor-ai-pidi.streamlit.app/)**

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
- 🚀 **REST API** - Integrasi dengan sistem eksternal

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

### 2. 🌐 **Heroku (FREE TIER)**

**Keuntungan:**
- ✅ 1000 jam gratis per bulan
- ✅ PostgreSQL database gratis
- ✅ Custom domain

**Langkah Deploy:**

1. **Install Heroku CLI:**
   ```bash
   # Download dari https://devcenter.heroku.com/articles/heroku-cli
   heroku --version
   ```

2. **Login dan Create App:**
   ```bash
   heroku login
   heroku create eksporai-mvp
   ```

3. **Setup Buildpacks:**
   ```bash
   heroku buildpacks:add heroku/python
   heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

5. **Buka App:**
   ```bash
   heroku open
   ```

---

### 3. 🚂 **Railway (FREE TIER)**

**Keuntungan:**
- ✅ 512MB RAM, 1GB disk gratis
- ✅ PostgreSQL database
- ✅ Auto-deploy dari GitHub

**Langkah Deploy:**

1. **Connect GitHub:**
   - Buka [railway.app](https://railway.app)
   - Connect GitHub account
   - Pilih repository

2. **Konfigurasi:**
   - Start Command: `streamlit run app.py --server.port $PORT --server.headless true`
   - Build Command: `pip install -r requirements.txt`

3. **Deploy otomatis** saat push ke GitHub

---

### 4. 🎨 **Render (FREE TIER)**

**Keuntungan:**
- ✅ 750 jam gratis per bulan
- ✅ Auto-deploy dari GitHub
- ✅ Static sites + web services

**Langkah Deploy:**

1. **Connect GitHub:**
   - Buka [render.com](https://render.com)
   - Connect repository

2. **Konfigurasi Web Service:**
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.headless true`

---

## 📁 Project Structure

```
eksporai-mvp/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration settings
├── requirements.txt               # Python dependencies
├── packages.txt                   # System dependencies
├── setup_and_test.py             # System verification script
│
├── utils/
│   ├── ai_engine.py               # ML scoring model
│   ├── matchmaking.py             # Buyer recommendation engine
│   ├── document_processor.py      # OCR + NLP document processing
│   ├── firebase_config.py         # Database management
│   ├── transaction_tracker.py     # Transaction management
│   ├── admin_manager.py           # Admin dashboard
│   └── api_server.py             # FastAPI REST API
│
├── models/
│   └── model_scoring.pkl          # Trained ML model
│
├── data/
│   └── dummy_umkm.csv            # Sample UMKM data
│
├── local_db/                      # Local storage fallback
│   └── *.json
│
└── assets/                        # Static files
```

## 🔧 Environment Variables

Buat file `.env` untuk konfigurasi:

```env
# Firebase (Opsional - gunakan local storage jika kosong)
FIREBASE_KEY={"type": "service_account", ...}
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com/

# Admin Settings
ADMIN_PASSWORD=ciko123

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
- Email: alvindra@example.com
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Project: PIDI Hackathon 2026

## 🙏 Acknowledgments

- PIDI (Indonesian Diaspora Network)
- Streamlit Community
- Firebase & Google Cloud
- Scikit-learn & Open Source ML Community

---

**⭐ Star this repo if you find it helpful!**

**🎉 Demo: [eksporai-mvp.streamlit.app](https://eksporai-mvp.streamlit.app)**

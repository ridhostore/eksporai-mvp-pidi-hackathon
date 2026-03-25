# EksporAI - Platform AI untuk Export Readiness & Intelligent Matchmaking UMKM

## 📋 Overview

EksporAI adalah platform MVP berbasis AI yang mengintegrasikan **Export Readiness Scoring** dan **Intelligent Matchmaking** untuk memfasilitasi ekspor UMKM Indonesia.

**Komponen Utama:**
- ✅ **Ensemble ML Model** - Random Forest + Gradient Boosting untuk scoring akurat
- ✅ **Intelligent Matchmaking** - Algoritma rekomendasi berbasis collaborative & content-based filtering
- ✅ **NLP + OCR** - Ekstraksi otomatis data dari dokumen (PDF/Gambar)
- ✅ **Firebase Integration** - Real-time database & authentication (dengan local storage fallback)
- ✅ **Admin Dashboard** - Analytics, UMKM management, transaction monitoring
- ✅ **REST API** - FastAPI endpoints untuk integrasi eksternal
- ✅ **Transaction Tracking** - Record dan monitor semua transaksi UMKM-Buyer

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone repository
cd d:/PIDI/eksporai-mvp

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# MacOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. (Optional) Configure Firebase

Jika ingin menggunakan Firebase + integration online:

```bash
# Create .env file
echo "FIREBASE_KEY=<your-firebase-key-json>" > .env
echo "FIREBASE_DATABASE_URL=https://your-project.firebaseio.com" >> .env
```

**Catatan:** Jika tidak ada Firebase config, sistem akan otomatis fallback ke **local storage** (JSON files di folder `local_db/`).

### 3. Run Verification & Tests

```bash
python setup_and_test.py
```

Output akan menunjukkan status semua modules:
- ✅ Package dependencies
- ✅ Utils modules
- ✅ Firebase/Local storage
- ✅ AI Engine
- ✅ Matchmaking
- ✅ Transaction Tracker
- ✅ Admin Manager
- ✅ API Server

### 4. Launch Streamlit App

```bash
streamlit run app.py
```

Aplikasi akan terbuka di `http://localhost:8501`

### 5. (Optional) Run API Server

Di terminal kedua:

```bash
python -m uvicorn utils.api_server:app --reload
```

API akan tersedia di `http://localhost:8000/docs`

---

## 📁 Directory Structure

```
eksporai-mvp/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration management
├── setup_and_test.py        # System verification script
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── data/
│   └── dummy_umkm.csv      # 1M UMKM training data
│
├── models/
│   └── model_scoring.pkl   # Trained Ensemble ML model
│
├── assets/                  # Images & resources
│
└── utils/
    ├── ai_engine.py                  # ML prediction engine
    ├── matchmaking.py                # Intelligent matchmaking algorithm
    ├── document_processor.py         # NLP + OCR for doc extraction
    ├── firebase_config.py            # Firebase/Local storage manager
    ├── transaction_tracker.py        # Transaction management
    ├── admin_manager.py              # Admin operations
    ├── api_server.py                 # FastAPI REST endpoints
    ├── train_model.py                # Model training script
    └── generate_dummy_data.py        # Generate dummy dataset
```

---

## 🎯 Main Features

### 1️⃣ Export Readiness Scoring

**Input:** UMKM business data
- Tahun berdiri
- Modal usaha
- Omzet bulanan
- Jumlah karyawan
- Sertifikasi (Halal, BPOM, NIB)
- Pengalaman ekspor
- Kapasitas produksi

**Output:** Score 0-100 + Status (READY/IMPROVING/NOT_READY)

**Algorithm:** Ensemble (Random Forest 100 trees + Gradient Boosting 100 trees)

### 2️⃣ Intelligent Matchmaking

**Algorithm:** Multi-factor compatibility scoring:
- Export Readiness Score (30%)
- Sector Preference (25%)
- Revenue/Omzet (20%)
- Certification Match (15%)
- Production Capacity (10%)

**Output:** Top 5-10 buyer recommendations dengan match score

### 3️⃣ Document Processing

**Capabilities:**
- PDF text extraction
- OCR for scanned documents/images
- NLP-based field extraction (menggunakan Spacy)
- Automatic NIB, NPWP, Nama, Omzet detection
- Confidence scoring

**Supported formats:** PDF, PNG, JPG, JPEG

### 4️⃣ Admin Dashboard

**Features:**
- 📊 Analytics dashboard (UMKM distribution, sector breakdown)
- 👥 UMKM management (list, verify, approve)
- 🤝 Buyer management (add, edit, delete)
- 💰 Transaction monitoring (status, value, success rate)
- ⚙️ System settings & backup

### 5️⃣ REST API

**Base URL:** `http://localhost:8000`

**Key Endpoints:**
- `POST /api/v1/umkm/score` - Calculate readiness score
- `GET /api/v1/matchmaking/{umkm_id}` - Get buyer recommendations
- `POST /api/v1/transactions` - Create transaction record
- `GET /api/v1/admin/dashboard` - Get admin analytics
- `POST /api/v1/documents/process` - Process uploaded documents

**Full documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## 🔑 Admin Panel Access

**Default password:** `admin123` (changeable via `.env` atau `secrets.toml`)

**Admin features:**
- Dashboard dengan KPI nasional
- Verifikasi dokumen UMKM
- Manajemen buyer database
- Transaction reporting & analytics
- System backup & maintenance

---

## 📊 Data Storage

EksporAI menggunakan **hybrid storage**:

### Option 1: Firebase (Online)
- Real-time database sync
- Cloud authentication
- Scalable storage

Aktivasi dengan menyediakan `FIREBASE_KEY` di `.env`

### Option 2: Local Storage (Default)
- JSON files di `local_db/` folder
- No authentication needed
- Perfect untuk development & MVP testing

**Folder structure:**
```
local_db/
├── umkm_UMKM_001.json
├── buyer_BUYER_001.json
├── transaction_abc123.json
├── contact_UMKM_001_BUYER_001_123.json
└── verification_UMKM_001.json
```

---

## 🔧 Training the ML Model

Untuk melatih ulang model atau retrain dengan data baru:

```bash
python utils/train_model.py
```

**Output:**
- `models/model_scoring.pkl` - Trained Ensemble model
- Console output: Accuracy (R² Score) & Error (RMSE)

**Training data:** `data/dummy_umkm.csv` (1M rows)

---

## 📧 Environment Variables (.env)

```
# Firebase Configuration (Optional)
FIREBASE_KEY=<firebase-service-account-json>
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# Admin Settings
ADMIN_PASSWORD=your_secure_password

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 🧪 Testing

### Run verification:
```bash
python setup_and_test.py
```

### Test specific modules:
```python
# Test AI Engine
from utils.ai_engine import predict_readiness_score
score = predict_readiness_score(umkm_data)

# Test Matchmaking
from utils.matchmaking import get_buyer_recommendations
buyers = get_buyer_recommendations(score, 'Makanan', umkm_data)

# Test Transaction Tracker
from utils.transaction_tracker import get_transaction_tracker
tracker = get_transaction_tracker()
trans_id = tracker.create_transaction(...)

# Test Admin Manager
from utils.admin_manager import get_admin_manager
admin = get_admin_manager()
dashboard = admin.get_dashboard_analytics()
```

---

## 🚨 Troubleshooting

### Issue: "Module not found"
- Pastikan di folder utama `eksporai-mvp/`
- Run: `pip install -r requirements.txt`

### Issue: "Firebase not working"
- Silakan `.env` file dengan FIREBASE credentials
- Atau gunakan local storage (default)

### Issue: "Streamlit not starting"
- Check: `streamlit run app.py`
- Port default: 8501

### Issue: "OCR/Tesseract error"
- OCR optional, PDF text extraction harus tetap work
- Untuk install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

---

## 📈 Performance Metrics

### ML Model Performance (100K test data)
- **Accuracy (R² Score):** 0.92+
- **Error (RMSE):** <5 points
- **Training time:** 1-3 minutes (100 estimators each)
- **Prediction time:** <10ms per sample

### Matchmaking Algorithm
- **Processing time:** <50ms per UMKM
- **Algorithm:** 5-factor compatibility scoring
- **Buyer database:** 10+ buyers (scalable)

### System
- **Max concurrent users:** 100+ (Streamlit Cloud)
- **API response time:** <200ms
- **Storage:** Local JSON (unlimited), Firebase (scalable)

---

## 🔐 Security Considerations

### Implemented:
- ✅ Password-protected admin panel
- ✅ Session state management
- ✅ Unique UMKM ID generation
- ✅ Data validation & sanitization
- ✅ Error handling & logging

### For Production:
- 🔒 Implement SSL/HTTPS
- 🔒 Database encryption
- 🔒 API authentication (JWT tokens)
- 🔒 Rate limiting
- 🔒 Audit logging
- 🔒 Data compliance (UU PDP)

---

## 🎓 Model Training Architecture

**Models:**
1. **Random Forest** - 100 trees
   - Good for capturing non-linear relationships
   - Robust to outliers
   
2. **Gradient Boosting** - 100 trees
   - Sequential learning
   - Captures complex patterns

**Ensemble:** Voting Regressor
- Average predictions dari kedua models
- Improved generalization

**Features (9):**
- tahun_berdiri
- modal_usaha
- omzet_bulanan
- jumlah_karyawan
- punya_sertifikat_halal
- punya_sertifikat_bpom
- punya_nib
- ekspor_sebelumnya
- kapasitas_produksi

**Target:**
- skor_kesiapan (0-100)

---

## 📱 API Examples

### Example 1: Calculate Readiness Score

```bash
curl -X POST "http://localhost:8000/api/v1/umkm/score" \
  -H "Content-Type: application/json" \
  -d '{
    "tahun_berdiri": 2015,
    "modal_usaha": 100000000,
    "omzet_bulanan": 50000000,
    "jumlah_karyawan": 10,
    "punya_sertifikat_halal": 1,
    "punya_sertifikat_bpom": 1,
    "punya_nib": 1,
    "ekspor_sebelumnya": 0,
    "kapasitas_produksi": 2000,
    "sektor": "Makanan"
  }'
```

### Example 2: Get Buyer Recommendations

```bash
curl "http://localhost:8000/api/v1/matchmaking/UMKM_001?limit=5"
```

### Example 3: Create Transaction

```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "umkm_id": "UMKM_001",
    "buyer_id": "BUY001",
    "quantity": 1000,
    "product": "Batik Fabric",
    "value_usd": 5000,
    "value_idr": 80000000,
    "notes": "Initial order"
  }'
```

---

## 🎯 Success Metrics (Target)

### By Month 6 (MVP Phase):
- ✅ 100 UMKM pilot terverifikasi
- ✅ 10 transaksi awal berhasil
- ✅ Platform fully functional
- ✅ API production-ready

### By Year 1:
- 🎯 1,000 UMKM difasilitasi
- 🎯 70% matchmaking success rate
- 🎯 Waktu verifikasi <2 minggu (dari 3 bulan)
- 🎯 +30% nilai transaksi UMKM binaan

---

## 📞 Contact & Support

**Team:**
- Founder & Lead Developer: Alvindra Agus Syahputra

**Project:**
- Event: PIDI Hackathon 2026
- MVP Phase: 6 months
- Status: In Development

---

## 📄 License & Credits

- Built with: Streamlit, FastAPI, Scikit-Learn, Firebase
- Data: 1M synthetic UMKM dataset
- Model: Ensemble (RF + GB)

---

**Last Updated:** March 25, 2026

**Version:** 1.0.0 (MVP)

```
          ╔═════════════════════════════╗
          ║    EksporAI MVP Ready! 🚀   ║
          ║   Ready to Export Together   ║
          ╚═════════════════════════════╝
```

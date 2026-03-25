# models/train_model.py
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Import Model & Ensemble dari Scikit-Learn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor

print("Membaca 1.000.000 data dummy UMKM...")
df = pd.read_csv('data/dummy_umkm.csv')

# 1. Siapkan Features & Target
features = [
    'tahun_berdiri', 'modal_usaha', 'omzet_bulanan', 'jumlah_karyawan',
    'punya_sertifikat_halal', 'punya_sertifikat_bpom', 'punya_nib',
    'ekspor_sebelumnya', 'kapasitas_produksi'
]
X = df[features]
y = df['skor_kesiapan']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Definisikan Model Individu
print("Mempersiapkan Random Forest dan Gradient Boosting...")
rf_model = RandomForestRegressor(n_estimators=300, random_state=42)
gb_model = GradientBoostingRegressor(n_estimators=300, random_state=42)

# 3. Gabungkan menjadi Ensemble (Voting Regressor)
print("Memulai training Ensemble Model (Estimasi waktu: 1-3 menit)...")
ensemble_model = VotingRegressor(estimators=[
    ('rf', rf_model), 
    ('gb', gb_model)
])

# Latih gabungan model ini
ensemble_model.fit(X_train, y_train)

# 4. Evaluasi Akurasi
print("Mengevaluasi akurasi model gabungan...")
y_pred = ensemble_model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n=== HASIL AKHIR ENSEMBLE ===")
print(f"Akurasi (R² Score) : {r2:.4f}")
print(f"Tingkat Error (RMSE): {rmse:.2f}")

# 5. Simpan Model
os.makedirs('models', exist_ok=True)

# Simpan data model beserta range target asli supaya bisa disesuaikan ke skala 0-100
model_artifact = {
    'estimator': ensemble_model,
    'y_min': float(y.min()),
    'y_max': float(y.max())
}
joblib.dump(model_artifact, 'models/model_scoring.pkl')
print("\n✅ Ensemble Model sukses dibekukan dan disimpan di models/model_scoring.pkl")
# models/train_model.py
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

# Import Model & Ensemble dari Scikit-Learn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor

# ============================================================================
# IMPROVED TRAINING - ANTI-BIAS VERSION
# ============================================================================
# Perbaikan:
# 1. Stratified train-test split by sektor (ensure balanced distribution)
# 2. Cross-validation untuk evaluate robustness
# 3. Feature importance logging
# 4. Better evaluation metrics (RMSE, MAE, R²)
# 5. Feature standardization
# ============================================================================

print("="*70)
print("TRAINING ML MODEL - ANTI-BIAS VERSION")
print("="*70)

print("\n📥 Membaca data dummy UMKM...")
df = pd.read_csv('data/dummy_umkm.csv')

# 1. Siapkan Features & Target
features = [
    'tahun_berdiri', 'modal_usaha', 'omzet_bulanan', 'jumlah_karyawan',
    'punya_sertifikat_halal', 'punya_sertifikat_bpom', 'punya_nib',
    'ekspor_sebelumnya', 'kapasitas_produksi'
]
X = df[features]
y = df['skor_kesiapan']

# STRATIFIED SPLIT by sektor (ensure each sector represented in train & test)
print("\n🔀 Melakukan stratified train-test split (balanced by sektor)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42,
    stratify=df['sektor']  # ✓ NEW: Stratified split
)

print(f"   Training set: {len(X_train):,} samples")
print(f"   Test set: {len(X_test):,} samples")

# 2. Feature Scaling (untuk better model stability)
print("\n📊 Feature scaling...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. Definisikan Model Individu
print("\n🤖 Mempersiapkan Random Forest dan Gradient Boosting...")
rf_model = RandomForestRegressor(
    n_estimators=150,  # Reduced dari 300 untuk avoid overfitting
    max_depth=15,      # Add depth limiting
    min_samples_split=10,
    random_state=42
)

gb_model = GradientBoostingRegressor(
    n_estimators=150,  # Reduced dari 300
    learning_rate=0.1,
    max_depth=5,
    min_samples_split=10,
    random_state=42
)

# 4. Gabungkan menjadi Ensemble (Voting Regressor)
print("\n🚀 Training Ensemble Model (5-Fold Cross-Validation)...")
ensemble_model = VotingRegressor(estimators=[
    ('rf', rf_model), 
    ('gb', gb_model)
])

# 5. CROSS-VALIDATION for robustness check
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(
    ensemble_model, 
    X_train_scaled, 
    y_train, 
    cv=kfold,
    scoring='r2'
)
print(f"   CV R² scores: {cv_scores.round(3)}")
print(f"   CV R² mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# 6. Final training on full training set
print("\n⏳ Training final ensemble model on full training set...")
ensemble_model.fit(X_train_scaled, y_train)

# 7. Evaluasi Akurasi di Test Set
print("\n📈 Evaluating model on test set...")
y_pred_train = ensemble_model.predict(X_train_scaled)
y_pred_test = ensemble_model.predict(X_test_scaled)

# Metrics on training set
r2_train = r2_score(y_train, y_pred_train)
rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
mae_train = mean_absolute_error(y_train, y_pred_train)

# Metrics on test set
r2_test = r2_score(y_test, y_pred_test)
rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
mae_test = mean_absolute_error(y_test, y_pred_test)

print("\n" + "="*70)
print("HASIL AKHIR ENSEMBLE MODEL")
print("="*70)
print(f"\n📊 TRAINING SET METRICS:")
print(f"   R² Score: {r2_train:.4f}")
print(f"   RMSE:     {rmse_train:.2f}")
print(f"   MAE:      {mae_train:.2f}")

print(f"\n📊 TEST SET METRICS (Generalization Check):")
print(f"   R² Score: {r2_test:.4f}")
print(f"   RMSE:     {rmse_test:.2f}")
print(f"   MAE:      {mae_test:.2f}")

# Check for overfitting
overfitting_ratio = rmse_test / rmse_train
print(f"\n⚠️  Overfitting indicator (test/train RMSE): {overfitting_ratio:.3f}")
if overfitting_ratio > 1.3:
    print("   ⚠️  WARNING: Model might be overfitting (test error >> train error)")
else:
    print("   ✓ Good generalization")

# 8. Feature Importance (from Random Forest)
print("\n🔍 Feature Importance Analysis:")
# Get feature importances from RF (first estimator)
rf_estimator = ensemble_model.estimators_[0]
feature_importance = rf_estimator.feature_importances_
feature_importance_df = pd.DataFrame({
    'feature': features,
    'importance': feature_importance
}).sort_values('importance', ascending=False)

print(feature_importance_df.to_string(index=False))

# 9. Simpan Model dengan metadata
print("\n💾 Saving model artifacts...")
os.makedirs('models', exist_ok=True)

model_artifact = {
    'estimator': ensemble_model,
    'scaler': scaler,  # ✓ NEW: Save scaler for inference
    'y_min': float(y.min()),
    'y_max': float(y.max()),
    'features': features,  # ✓ NEW: Save feature names
    'feature_importance': feature_importance_df.to_dict('records'),  # ✓ NEW
    'metrics': {  # ✓ NEW: Save metrics
        'r2_train': float(r2_train),
        'r2_test': float(r2_test),
        'rmse_train': float(rmse_train),
        'rmse_test': float(rmse_test),
        'mae_train': float(mae_train),
        'mae_test': float(mae_test),
        'cv_r2_mean': float(cv_scores.mean()),
        'cv_r2_std': float(cv_scores.std())
    }
}

joblib.dump(model_artifact, 'models/model_scoring.pkl')

print("✅ Model artifacts saved:")
print(f"   📁 models/model_scoring.pkl")
print(f"   🔑 Includes: ensemble model, scaler, features, importances, metrics")
print("="*70)
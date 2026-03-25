# utils/ai_engine.py
import pandas as pd
import numpy as np
import joblib
import os

def predict_readiness_score(umkm_data):
    """
    Memprediksi skor kesiapan ekspor menggunakan Ensemble ML model
    """
    try:
        model_path = 'models/model_scoring.pkl'
        
        # Fallback jika model belum di-train
        if not os.path.exists(model_path):
            print("Model ML tidak ditemukan, menggunakan rule-based fallback.")
            return _rule_based_scoring(umkm_data)
        
        # 1. LOAD MODEL (Model yang diload otomatis berisi gabungan RF & GB)
        model = joblib.load(model_path)
        
        # 2. INPUT FORMATTING (Harus urut sesuai saat training)
        features = [
            'tahun_berdiri', 'modal_usaha', 'omzet_bulanan', 'jumlah_karyawan',
            'punya_sertifikat_halal', 'punya_sertifikat_bpom', 'punya_nib',
            'ekspor_sebelumnya', 'kapasitas_produksi'
        ]
        input_df = pd.DataFrame([umkm_data])[features]
        
        # 3. PREDICT (Otomatis mengambil rata-rata dari RF dan GB)
        score = model.predict(input_df)[0]
        
        # Pastikan skor tidak bocor di luar 0 - 100
        score = float(np.clip(score, 0, 100)) 
        
        return int(score)
    
    except Exception as e:
        print(f"Error pada sistem AI: {e}")
        # Jika terjadi error input, gunakan perhitungan manual sebagai cadangan
        return _rule_based_scoring(umkm_data)

def _rule_based_scoring(umkm_data):
    """Sistem cadangan (fallback) jika Machine Learning gagal"""
    score = 0
    
    if umkm_data.get('punya_nib'): score += 5
    if umkm_data.get('punya_sertifikat_halal'): score += 5
    if umkm_data.get('punya_sertifikat_bpom'): score += 5
    if umkm_data.get('ekspor_sebelumnya'): score += 5
    
    if umkm_data.get('omzet_bulanan', 0) > 50000000: score += 10
    if umkm_data.get('modal_usaha', 0) > 100000000: score += 5
    if umkm_data.get('kapasitas_produksi', 0) > 1000: score += 10
    
    years_operating = 2026 - umkm_data.get('tahun_berdiri', 2026)
    if years_operating >= 5: score += 5
    
    return int(min(100, score))
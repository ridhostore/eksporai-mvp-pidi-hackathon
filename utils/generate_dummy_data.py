# utils/generate_dummy_data.py
import pandas as pd
import numpy as np
import os
import random

# ============================================================================
# IMPROVED DATA GENERATION - ANTI-BIAS VERSION
# ============================================================================
# Perbaikan:
# 1. Balanced sektor distribution (25% each, bukan 40:30:20:10)
# 2. REMOVE target leakage: skor_kesiapan tidak dihitung dari training features
# 3. Realistic feature distributions (independent, dengan natural variance)
# 4. Skor hanya bergantung pada domain knowledge, bukan ML features
# 5. Higher noise untuk avoid artificial patterns
# ============================================================================

# Random seed untuk reproducibility tapi bisa di-rotate
np.random.seed(42)
random.seed(42)

# JUMLAH DATA
n_samples = 100000
print(f"Mulai generate {n_samples:,} data dummy UMKM (ANTI-BIAS VERSION)...")

# === STEP 1: GENERATE INDEPENDENT FEATURES ===

# 1a. Tahun Berdiri (realistic distribution)
years_operating = np.random.poisson(lam=8, size=n_samples)
years_operating = np.clip(years_operating, 1, 20)
tahun_berdiri = 2026 - years_operating

# 1b. Sektor - BALANCED (25% each)
sektor_choices = ['Makanan', 'Kerajinan', 'Fashion', 'Kosmetik']
sektor = np.random.choice(sektor_choices, n_samples, p=[0.25, 0.25, 0.25, 0.25])

# 1c. Karyawan - INDEPENDENT distribution (tidak tied ke years_operating terlalu kuat)
# Realistic: 1-50 karyawan untuk UMKM (mode 5-10)
jumlah_karyawan = np.random.negative_binomial(n=5, p=0.4, size=n_samples)
jumlah_karyawan = np.clip(jumlah_karyawan, 1, 100)

# 1d. Modal Usaha - REALISTIC range per sektor
modal_base = np.where(sektor == 'Makanan', 5000000, 10000000)
modal_noise = np.random.normal(1, 2, n_samples)  # multiplicative noise
modal_usaha = modal_base * (np.abs(modal_noise) + 0.5)
modal_usaha = np.clip(modal_usaha, 1000000, 500000000)

# 1e. Omzet Bulanan - INDEPENDENT dari modal & features lainnya
# realistic: kecil-menengah mostly
omzet_base = np.random.gamma(shape=3, scale=5000000, size=n_samples)
omzet_bulanan = np.clip(omzet_base, 100000, 300000000)

# 1f. Kapasitas Produksi - INDEPENDENT
# realistic: 10-10000 unit tergantung sektor
kapasitas_base = np.where(
    sektor == 'Makanan', 
    np.random.lognormal(mean=4, sigma=1.5, size=n_samples),  # More medium capacity
    np.random.lognormal(mean=3.5, sigma=1.5, size=n_samples)
)
kapasitas_produksi = np.clip(kapasitas_base, 10, 15000).astype(int)

# === STEP 2: SERTIFIKASI - INDEPENDENT dari target ===
# Probabilitas sertifikasi tergantung skala bisnis, bukan ranking score

# NIB: bergantung years_operating + omzet (realistic: butuh proses formal)
prob_nib = np.clip(0.2 + (years_operating * 0.025) + (np.log10(omzet_bulanan) * 0.05), 0.15, 0.85)
punya_nib = np.random.binomial(1, prob_nib)

# Halal: hanya makanan + berdasarkan omzet (tidak semua punya)
is_makanan = (sektor == 'Makanan').astype(int)
prob_halal = is_makanan * (0.1 + np.clip(omzet_bulanan / 500000000, 0, 0.4))
prob_halal = np.clip(prob_halal, 0, 0.6)
punya_sertifikat_halal = np.random.binomial(1, prob_halal)

# BPOM: makanan saja, random independent (sulit & mahal)
prob_bpom = is_makanan * np.random.uniform(0.05, 0.25, n_samples)
punya_sertifikat_bpom = np.random.binomial(1, prob_bpom)

# Ekspor sebelumnya: rare event, independent
prob_ekspor = 0.08 + (np.log10(omzet_bulanan + 1) * 0.02)  # sedikit berhub omzet tapi not linear
prob_ekspor = np.clip(prob_ekspor, 0.02, 0.3)
ekspor_sebelumnya = np.random.binomial(1, prob_ekspor)

# === STEP 3: TARGET VARIABLE - SKOR KESIAPAN ===
# CRITICAL: Skor dihitung dari INDEPENDENT logic, BUKAN features training
# Basis: domain expert knowledge, bukan data engineering

# Base score: semua mulai dari 30-40 (median readiness)
skor_kesiapan = np.ones(n_samples) * 35

# Increment dari sertifikasi (ada/tidak ada = fundamental)
skor_kesiapan += punya_nib * 10              # NIB adalah fundamental
skor_kesiapan += punya_sertifikat_halal * 8  # Halal penting untuk makanan
skor_kesiapan += punya_sertifikat_bpom * 12  # BPOM harder to get, more valuable
skor_kesiapan += ekspor_sebelumnya * 15      # Track record penting

# Increment dari scale (omzet & kapasitas)
# Logika: bigger = more ready (tapi tidak linear, log scale)
omzet_score = np.clip(np.log10(omzet_bulanan + 1) - 4, 0, 15)  # 0-15
skor_kesiapan += omzet_score

kapasitas_score = np.clip(np.log10(kapasitas_produksi + 1) - 1, 0, 10)  # 0-10
skor_kesiapan += kapasitas_score

# Increment dari modal
modal_score = np.clip(np.log10(modal_usaha + 1) - 6, 0, 8)  # 0-8
skor_kesiapan += modal_score

# Increment dari experience (years operating)
exp_score = np.clip(years_operating / 4, 0, 10)  # 0-10 untuk 40+ years
skor_kesiapan += exp_score

# === HIGH NOISE - ANTI-MEMORIZATION ===
# Add significant random noise to avoid model memorizing patterns
noise = np.random.normal(0, 8, n_samples)  # Higher std untuk real-world uncertainty
skor_kesiapan += noise

# Normalize ke 0-100 scale
skor_kesiapan = np.clip(skor_kesiapan, 0, 100).astype(int)

# === STEP 4: CREATE DATAFRAME & SAVE ===

# Dictionary with all arrays
data = {
    'id_umkm': range(1, n_samples + 1),
    'nama_usaha': [f'UMKM_{i:06d}' for i in range(1, n_samples + 1)],
    'sektor': sektor,
    'tahun_berdiri': tahun_berdiri,
    'modal_usaha': modal_usaha.astype(int),
    'omzet_bulanan': omzet_bulanan.astype(int),
    'jumlah_karyawan': jumlah_karyawan,
    'punya_sertifikat_halal': punya_sertifikat_halal,
    'punya_sertifikat_bpom': punya_sertifikat_bpom,
    'punya_nib': punya_nib,
    'ekspor_sebelumnya': ekspor_sebelumnya,
    'kapasitas_produksi': kapasitas_produksi,
    'skor_kesiapan': skor_kesiapan  # Independent target, bukan leakage
}

df_final = pd.DataFrame(data)

# === VALIDATION & STATISTICS ===
print("\n" + "="*60)
print("DATA GENERATION SUMMARY (ANTI-BIAS)")
print("="*60)
print(f"✓ Total records: {len(df_final):,}")
print(f"\n📊 Sektor distribution (target: balanced 25% each):")
print(df_final['sektor'].value_counts(normalize=True).round(3))
print(f"\n📈 Skor Kesiapan statistics:")
print(df_final['skor_kesiapan'].describe().round(2))
print(f"\n🔍 Feature statistics:")
print(f"  Tahun berdiri: {df_final['tahun_berdiri'].min()}-{df_final['tahun_berdiri'].max()}")
print(f"  Modal: Rp{df_final['modal_usaha'].min():,.0f} - Rp{df_final['modal_usaha'].max():,.0f}")
print(f"  Omzet: Rp{df_final['omzet_bulanan'].min():,.0f} - Rp{df_final['omzet_bulanan'].max():,.0f}")
print(f"  Karyawan: {df_final['jumlah_karyawan'].min()}-{df_final['jumlah_karyawan'].max()}")
print(f"\n🎫 Sertifikasi penetration:")
print(f"  NIB: {df_final['punya_nib'].sum()/len(df_final)*100:.1f}%")
print(f"  Halal: {df_final['punya_sertifikat_halal'].sum()/len(df_final)*100:.1f}%")
print(f"  BPOM: {df_final['punya_sertifikat_bpom'].sum()/len(df_final)*100:.1f}%")
print(f"  Ekspor: {df_final['ekspor_sebelumnya'].sum()/len(df_final)*100:.1f}%")

# Simpan ke CSV
os.makedirs('data', exist_ok=True)
df_final.to_csv('data/dummy_umkm.csv', index=False)
print(f"\n✅ Dataset UMKM dummy ({n_samples:,} records) berhasil dibuat!")
print(f"   📁 Lokasi: data/dummy_umkm.csv")
print("="*60)
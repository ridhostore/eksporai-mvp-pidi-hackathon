# utils/generate_dummy_data.py
import pandas as pd
import numpy as np
import os
import random

# Set seed agar hasilnya konsisten
np.random.seed(42)
random.seed(42)

# JUMLAH DATA: 100,000
n_samples = 100000
print(f"Mulai generate {n_samples:,} data dummy UMKM...")

# === A. Membuat Data Dummy yang Saling Terkait (Coherent) ===

# 1. Tahun Berdiri
years_operating = np.random.poisson(lam=7, size=n_samples)
years_operating = np.clip(years_operating, 1, 16)
tahun_berdiri = 2026 - years_operating

# 2. Sektor
sektor_choices = ['Makanan', 'Kerajinan', 'Fashion', 'Kosmetik']
sektor = np.random.choice(sektor_choices, n_samples, p=[0.4, 0.3, 0.2, 0.1])

# 3. Karyawan
jumlah_karyawan = np.random.poisson(lam=(years_operating * 2), size=n_samples)
jumlah_karyawan = np.clip(jumlah_karyawan, 1, 100)

# 4. Modal Usaha
base_modal = np.where(sektor == 'Makanan', 10000000, 25000000)
modal_usaha = base_modal + (jumlah_karyawan * 5000000) + np.random.normal(0, 10000000, n_samples)
modal_usaha = np.clip(modal_usaha, 1, 1000000000)

# 5. Omzet Bulanan
roi = np.random.uniform(0.05, 0.15, n_samples)
omzet_bulanan = (modal_usaha * roi) + (jumlah_karyawan * 1000000) + np.random.normal(0, 5000000, n_samples)
omzet_bulanan = np.clip(omzet_bulanan, 1, 500000000)

# 6. Kapasitas Produksi
kapasitas_produksi = np.where(sektor == 'Makanan', omzet_bulanan / 20000, omzet_bulanan / 50000)
kapasitas_produksi += np.random.normal(0, 500, n_samples)
kapasitas_produksi = np.clip(kapasitas_produksi, 1, 20000).astype(int)

# 7. Sertifikasi (PERBAIKAN LOGIKA & URUTAN)
# Hitung probabilitas dan array 'punya_nib' DULU
prob_nib = np.clip(0.5 + (years_operating * 0.03), 0.2, 0.95)
punya_nib = np.random.binomial(1, prob_nib)

prob_halal = np.clip(0.3 + (np.where(sektor == 'Makanan', 0.4, 0)) + (omzet_bulanan / 200000000), 0.1, 0.9)
punya_sertifikat_halal = np.random.binomial(1, prob_halal)

prob_bpom = np.clip(0.2 + (np.where(sektor == 'Makanan', 0.5, 0)) + (omzet_bulanan / 300000000), 0.1, 0.9)
punya_sertifikat_bpom = np.random.binomial(1, prob_bpom)

# Sekarang kita gunakan array numpy 'punya_nib', bukan df['punya_nib']
prob_ekspor = np.clip(0.05 + (omzet_bulanan / 400000000) + (punya_nib * 0.1), 0.01, 0.4)
ekspor_sebelumnya = np.random.binomial(1, prob_ekspor)

# === B. Membuat Skor Kesiapan Ekspor yang Logis ===

scores = np.ones(n_samples) * 20 

scores += punya_nib * 5
scores += punya_sertifikat_halal * 5
scores += punya_sertifikat_bpom * 5
scores += ekspor_sebelumnya * 5

scores += np.clip(np.log10(omzet_bulanan) * 3, 0, 20)
scores += np.clip(np.log10(modal_usaha) * 1.5, 0, 10)
scores += np.clip(years_operating * 1, 0, 10)

scores += np.random.normal(0, 2, n_samples)

# Simpan skor akhir ke dalam array numpy (bukan DataFrame)
skor_kesiapan_final = np.clip(scores, 0, 100).astype(int)

# === C. Finalisasi & Penyimpanan ===

# Gabungkan semua array numpy ke dalam dictionary, LALU jadikan DataFrame
data = {
    'id_umkm': range(1, n_samples + 1),
    'nama_usaha': [f'UMKM {i}' for i in range(1, n_samples + 1)],
    'sektor': sektor,
    'tahun_berdiri': tahun_berdiri,
    'modal_usaha': modal_usaha,
    'omzet_bulanan': omzet_bulanan,
    'jumlah_karyawan': jumlah_karyawan,
    'punya_sertifikat_halal': punya_sertifikat_halal,
    'punya_sertifikat_bpom': punya_sertifikat_bpom,
    'punya_nib': punya_nib,
    'ekspor_sebelumnya': ekspor_sebelumnya,
    'kapasitas_produksi': kapasitas_produksi,
    'skor_kesiapan': skor_kesiapan_final # Menggunakan array numpy
}

df_final = pd.DataFrame(data)

# Simpan ke CSV
os.makedirs('data', exist_ok=True)
df_final.to_csv('data/dummy_umkm.csv', index=False)
print(f"Dataset UMKM dummy ({n_samples:,} data) berhasil dibuat di data/dummy_umkm.csv!")
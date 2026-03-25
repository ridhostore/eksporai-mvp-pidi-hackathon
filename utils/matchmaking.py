# utils/matchmaking.py
"""
Intelligent Matchmaking Engine dengan Collaborative Filtering & Content-Based
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json
import os

class IntelligentMatcher:
    """Sistem rekomendasi UMKM-Buyer berbasis AI"""
    
    def __init__(self):
        self.buyers_db = self._load_buyer_database()
        self.umkm_history = {}
    
    def _load_buyer_database(self):
        """Load buyer database dari lokal atau Firebase"""
        return [
            {
                "id": "BUY001",
                "nama": "Tokyo Import Co., Ltd.",
                "negara": "🇯🇵 Jepang",
                "jenis_perusahaan": "Importir Kerajinan",
                "min_order": 1000,
                "deskripsi": "Spesialis produk dekorasi rumah tradisional Indonesia",
                "preferensi_sektor": ["Kerajinan", "Fashion"],
                "min_score": 75,
                "rating": 4.8,
                "transaksi_sukses": 245,
                "kategori_produk": ["Dekorasi", "Furniture", "Aksesori"],
                "min_omzet_supplier": 10000000,
                "preferensi_sertifikasi": ["Halal", "Export"]
            },
            {
                "id": "BUY002",
                "nama": "Berlin Organic Foods GmbH",
                "negara": "🇩🇪 Jerman",
                "jenis_perusahaan": "Retailer Makanan",
                "min_order": 500,
                "deskripsi": "Fokus pada produk camilan organik dan sehat",
                "preferensi_sektor": ["Makanan", "Kosmetik"],
                "min_score": 70,
                "rating": 4.6,
                "transaksi_sukses": 189,
                "kategori_produk": ["Snack", "Minuman", "Herbal"],
                "min_omzet_supplier": 20000000,
                "preferensi_sertifikasi": ["Halal", "BPOM", "Organik"]
            },
            {
                "id": "BUY003",
                "nama": "Singapore Trading Hub Pte Ltd",
                "negara": "🇸🇬 Singapura",
                "jenis_perusahaan": "Distributor Umum",
                "min_order": 300,
                "deskripsi": "Gateway untuk distribusi ke Asia Tenggara",
                "preferensi_sektor": ["Makanan", "Kerajinan", "Fashion", "Kosmetik"],
                "min_score": 60,
                "rating": 4.7,
                "transaksi_sukses": 512,
                "kategori_produk": ["Semua kategori"],
                "min_omzet_supplier": 5000000,
                "preferensi_sertifikasi": []
            },
            {
                "id": "BUY004",
                "nama": "New York Fashion Wholesale Inc.",
                "negara": "🇺🇸 USA",
                "jenis_perusahaan": "Distributor Fashion",
                "min_order": 2000,
                "deskripsi": "Spesialis fashion Indonesia & sustainable products",
                "preferensi_sektor": ["Fashion", "Kerajinan"],
                "min_score": 78,
                "rating": 4.9,
                "transaksi_sukses": 127,
                "kategori_produk": ["Pakaian", "Aksesori Fashion", "Tas"],
                "min_omzet_supplier": 50000000,
                "preferensi_sertifikasi": ["Export Ready"]
            },
            {
                "id": "BUY005",
                "nama": "Dubai Trading Company LLC",
                "negara": "🇦🇪 UAE",
                "jenis_perusahaan": "Trader Umum",
                "min_order": 800,
                "deskripsi": "Distributor produk halal ke pasar Timur Tengah",
                "preferensi_sektor": ["Makanan", "Kosmetik", "Kerajinan"],
                "min_score": 65,
                "rating": 4.5,
                "transaksi_sukses": 380,
                "kategori_produk": ["Makanan Halal", "Kosmetik", "Kerajinan"],
                "min_omzet_supplier": 15000000,
                "preferensi_sertifikasi": ["Halal"]
            },
            {
                "id": "BUY006",
                "nama": "Paris Beauty Supplies Ltd",
                "negara": "🇫🇷 Prancis",
                "jenis_perusahaan": "Importer Kosmetik",
                "min_order": 400,
                "deskripsi": "Natural & organic cosmetics khusus dari Asia",
                "preferensi_sektor": ["Kosmetik"],
                "min_score": 72,
                "rating": 4.7,
                "transaksi_sukses": 156,
                "kategori_produk": ["Skincare", "Body Care", "Makeup"],
                "min_omzet_supplier": 25000000,
                "preferensi_sertifikasi": ["BPOM", "Export"]
            },
            {
                "id": "BUY007",
                "nama": "Bangkok Food Distribution Co.",
                "negara": "🇹🇭 Thailand",
                "jenis_perusahaan": "Distributor Makanan",
                "min_order": 600,
                "deskripsi": "Gateway ASEAN untuk produk makanan premium",
                "preferensi_sektor": ["Makanan"],
                "min_score": 61,
                "rating": 4.4,
                "transaksi_sukses": 234,
                "kategori_produk": ["Snack", "Sauce", "Beverage"],
                "min_omzet_supplier": 8000000,
                "preferensi_sertifikasi": ["Halal"]
            },
            {
                "id": "BUY008",
                "nama": "London Crafts International",
                "negara": "🇬🇧 Inggris",
                "jenis_perusahaan": "Importir Kerajinan",
                "min_order": 1500,
                "deskripsi": "Produk kerajinan tangan autentik untuk pasar Eropa",
                "preferensi_sektor": ["Kerajinan", "Fashion"],
                "min_score": 76,
                "rating": 4.8,
                "transaksi_sukses": 98,
                "kategori_produk": ["Batik", "Woodcraft", "Textile"],
                "min_omzet_supplier": 30000000,
                "preferensi_sertifikasi": ["Export"]
            },
            {
                "id": "BUY009",
                "nama": "Seoul Tech Export Hub",
                "negara": "🇰🇷 Korea",
                "jenis_perusahaan": "E-Commerce Distributor",
                "min_order": 250,
                "deskripsi": "Platform e-commerce Asia untuk UMKM berkualitas",
                "preferensi_sektor": ["Fashion", "Kerajinan", "Kosmetik"],
                "min_score": 55,
                "rating": 4.6,
                "transaksi_sukses": 678,
                "kategori_produk": ["Fashion", "Accessories", "Beauty"],
                "min_omzet_supplier": 3000000,
                "preferensi_sertifikasi": []
            },
            {
                "id": "BUY010",
                "nama": "Melbourne Coffee & Tea Co.",
                "negara": "🇦🇺 Australia",
                "jenis_perusahaan": "Specialty Importer",
                "min_order": 200,
                "deskripsi": "Produk specialty Indonesia untuk market Australia",
                "preferensi_sektor": ["Makanan"],
                "min_score": 58,
                "rating": 4.5,
                "transaksi_sukses": 145,
                "kategori_produk": ["Kopi", "Teh", "Specialty Foods"],
                "min_omzet_supplier": 12000000,
                "preferensi_sertifikasi": ["Export"]
            }
        ]
    
    def calculate_compatibility_score(self, umkm_data, buyer):
        """
        Hitung compatibility score antara UMKM dan Buyer
        Menggunakan multiple factors: score, sektor, omzet, sertifikasi
        """
        score = 0
        max_score = 100
        
        # 1. Export Readiness Score Matching (30 points)
        if umkm_data.get('skor_kesiapan', 0) >= buyer['min_score']:
            score += 30
        else:
            score += (umkm_data.get('skor_kesiapan', 0) / buyer['min_score']) * 30
        
        # 2. Sector Preference Matching (25 points)
        if umkm_data.get('sektor') in buyer['preferensi_sektor']:
            score += 25
        elif buyer['preferensi_sektor'] == ["Semua kategori"]:
            score += 20
        else:
            score += 5
        
        # 3. Revenue/Omzet Matching (20 points)
        if umkm_data.get('omzet_bulanan', 0) >= buyer['min_omzet_supplier']:
            score += 20
        elif umkm_data.get('omzet_bulanan', 0) >= (buyer['min_omzet_supplier'] * 0.7):
            score += 15
        else:
            score += (umkm_data.get('omzet_bulanan', 0) / buyer['min_omzet_supplier']) * 20
        
        # 4. Certification Matching (15 points)
        certs_count = 0
        if umkm_data.get('punya_sertifikat_halal') == 1:
            certs_count += 1
        if umkm_data.get('punya_sertifikat_bpom') == 1:
            certs_count += 1
        if umkm_data.get('punya_nib') == 1:
            certs_count += 1
        
        if buyer['preferensi_sertifikasi']:
            required_certs = len(buyer['preferensi_sertifikasi'])
            score += (certs_count / required_certs) * 15 if required_certs > 0 else 15
        else:
            score += certs_count * 5
        
        # 5. Production Capacity Matching (10 points)
        if umkm_data.get('kapasitas_produksi', 0) >= buyer['min_order']:
            score += 10
        elif umkm_data.get('kapasitas_produksi', 0) >= (buyer['min_order'] * 0.5):
            score += 5
        
        return min(100, int(score))
    
    def get_recommendations(self, umkm_data, top_n=5):
        """
        Dapatkan rekomendasi buyer terbaik untuk UMKM
        """
        # Filter by minimum score requirement
        eligible_buyers = [
            buyer for buyer in self.buyers_db 
            if umkm_data.get('skor_kesiapan', 0) >= buyer['min_score'] - 5
        ]
        
        # Calculate compatibility untuk setiap buyer
        recommendations = []
        for buyer in eligible_buyers:
            compat_score = self.calculate_compatibility_score(umkm_data, buyer)
            buyer_with_score = buyer.copy()
            buyer_with_score['match_score'] = compat_score
            recommendations.append(buyer_with_score)
        
        # Sort by compatibility score (descending)
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:top_n]
    
    def add_user_interaction(self, umkm_id, buyer_id, interaction_type, success):
        """Track user interaction untuk improvement recommendation algorithm"""
        key = f"{umkm_id}_{buyer_id}"
        if key not in self.umkm_history:
            self.umkm_history[key] = []
        
        self.umkm_history[key].append({
            'interaction': interaction_type,
            'success': success,
            'timestamp': pd.Timestamp.now().isoformat()
        })


# Global matcher instance
matcher = IntelligentMatcher()


def get_buyer_recommendations(score, sektor="Makanan", umkm_data=None, top_n=5):
    """
    Legacy function wrapper untuk backward compatibility
    
    Parameters:
    score (int): UMKM readiness score (0-100)
    sektor (str): Business sector
    umkm_data (dict): Full UMKM data untuk intelligent matching
    top_n (int): Number of recommendations to return
    
    Returns:
    list: List of buyer dictionaries dengan match scores
    """
    if umkm_data is None:
        umkm_data = {
            'skor_kesiapan': score,
            'sektor': sektor,
            'omzet_bulanan': 10000000,
            'punya_sertifikat_halal': 0,
            'punya_sertifikat_bpom': 0,
            'punya_nib': 1,
            'kapasitas_produksi': 500
        }
    
    return matcher.get_recommendations(umkm_data, top_n)

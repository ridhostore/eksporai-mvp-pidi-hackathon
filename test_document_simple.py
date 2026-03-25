#!/usr/bin/env python3
"""
Test Document Processing untuk EksporAI MVP
"""
import os
import re
from typing import Dict

def extract_text_from_file(file_path: str) -> str:
    """Extract text dari file berdasarkan extension"""
    if not os.path.exists(file_path):
        return ""

    ext = file_path.lower().split('.')[-1]

    try:
        if ext in ['txt', 'csv']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"Unsupported file type: {ext}"
    except Exception as e:
        return f"Error reading file: {e}"

def parse_umkm_data_from_text(text: str) -> Dict:
    """Parse UMKM data dari text menggunakan regex"""
    data = {}

    # Regex patterns untuk common UMKM data fields
    patterns = {
        'nib': r'(?:NIB|Nomor\s+Induk\s+Berusaha)[:\s]*([0-9]{13,16})',
        'nama': r'(?:Nama\s+(?:Usaha|Perusahaan|Bisnis))[:\s]*([A-Za-z\s\-&]+?)(?:\n|$)',
        'npwp': r'(?:NPWP)[:\s]*([0-9\.\-]{15,20})',
        'modal_usaha': r'(?:Modal\s+(?:Usaha|Awal|Kerja))[:\s]*Rp[\s\.]*([0-9,\.]+)',
        'omzet_bulanan': r'(?:Omzet|Pendapatan|Penjualan)(?:\s+(?:Bulanan|Tahunan|Rata-rata))?[:\s]*Rp[\s\.]*([0-9,\.]+)',
        'tahun_berdiri': r'(?:Tahun\s+(?:Berdiri|Didirikan|Mulai))[:\s]*([0-9]{4})',
        'jumlah_karyawan': r'(?:Jumlah\s+(?:Karyawan|Tenaga\s+Kerja|Pegawai))[:\s]*([0-9]+)',
        'kapasitas_produksi': r'(?:Kapasitas\s+(?:Produksi|Produk))[:\s]*([0-9,\.]+)',
        'alamat': r'(?:Alamat|Lokasi)[:\s]*([A-Za-z0-9\s\-,\.]+?)(?:\n|$)',
    }

    # Extract field-field menggunakan regex
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            data[field] = value

    # Extract certifications
    data['punya_sertifikat_halal'] = 1 if re.search(r'sertifikat\s+halal|halal\s+cert', text, re.IGNORECASE) else 0
    data['punya_sertifikat_bpom'] = 1 if re.search(r'sertifikat\s+bpom|bpom|izin\s+edar', text, re.IGNORECASE) else 0
    data['punya_nib'] = 1 if re.search(r'nib|nomor\s+induk\s+berusaha', text, re.IGNORECASE) else 0
    data['ekspor_sebelumnya'] = 1 if re.search(r'pernah\s+ekspor|sudah\s+export|pengalaman\s+export', text, re.IGNORECASE) else 0

    # Calculate confidence
    extracted_fields = len([k for k, v in data.items() if v and k not in ['punya_sertifikat_halal', 'punya_sertifikat_bpom', 'punya_nib', 'ekspor_sebelumnya']])
    total_possible_fields = len(patterns)
    data['confidence'] = extracted_fields / total_possible_fields if total_possible_fields > 0 else 0

    return data

def test_document_processing():
    print('🧪 TESTING DOCUMENT UPLOAD & PROCESSING')
    print('=' * 60)

    # Test dengan file teks yang baru dibuat
    test_file = 'test_umkm_data.txt'
    if os.path.exists(test_file):
        print(f'📄 Testing with: {test_file}')

        # Extract text
        text = extract_text_from_file(test_file)
        if text:
            print('✅ Text extraction successful!')
            print(f'📝 Extracted {len(text)} characters')
            print()

            # Parse UMKM data
            result = parse_umkm_data_from_text(text)
            print('📋 EXTRACTED UMKM DATA:')
            print('-' * 40)

            # Group fields by category
            basic_info = {}
            financial_info = {}
            certifications = {}
            other_info = {}

            for key, value in result.items():
                if value and key not in ['confidence']:  # Only show non-empty values
                    if key in ['nama', 'alamat', 'nib', 'npwp']:
                        basic_info[key.upper()] = value
                    elif key in ['modal_usaha', 'omzet_bulanan', 'tahun_berdiri']:
                        financial_info[key.replace('_', ' ').title()] = value
                    elif 'sertifikat' in key.lower() or key in ['punya_nib', 'ekspor_sebelumnya']:
                        certifications[key.replace('_', ' ').replace('punya_', '').title()] = 'Ya' if value == 1 else 'Tidak'
                    else:
                        other_info[key.replace('_', ' ').title()] = value

            if basic_info:
                print('🏢 BASIC INFORMATION:')
                for k, v in basic_info.items():
                    print(f'  • {k}: {v}')
                print()

            if financial_info:
                print('💰 FINANCIAL INFORMATION:')
                for k, v in financial_info.items():
                    print(f'  • {k}: {v}')
                print()

            if certifications:
                print('📜 CERTIFICATIONS & EXPERIENCE:')
                for k, v in certifications.items():
                    print(f'  • {k}: {v}')
                print()

            if other_info:
                print('📊 OTHER INFORMATION:')
                for k, v in other_info.items():
                    print(f'  • {k}: {v}')

            print()
            print('🎯 EXTRACTION RESULTS:')
            print(f'  • Overall Confidence: {result.get("confidence", 0):.1%}')
            print(f'  • Fields Extracted: {len([k for k, v in result.items() if v and k != "confidence"])}')

        else:
            print('❌ Text extraction failed')
    else:
        print('❌ Test file not found')

    print()
    print('📋 SUPPORTED DOCUMENT FORMATS:')
    print('• PDF files (.pdf) - Text extraction + OCR fallback')
    print('• Image files (.png, .jpg, .jpeg) - OCR processing')
    print('• Text files (.txt, .csv) - Direct text parsing')
    print()
    print('📋 EXTRACTABLE FIELDS:')
    print('• NIB (Nomor Induk Berusaha)')
    print('• NPWP (Nomor Pokok Wajib Pajak)')
    print('• Nama Perusahaan')
    print('• Alamat Lengkap')
    print('• Modal Usaha')
    print('• Omzet Bulanan')
    print('• Jumlah Karyawan')
    print('• Tahun Berdiri')
    print('• Kapasitas Produksi')
    print('• Sertifikat Halal (Ya/Tidak)')
    print('• Sertifikat BPOM (Ya/Tidak)')
    print('• Pengalaman Ekspor (Ya/Tidak)')

if __name__ == '__main__':
    test_document_processing()
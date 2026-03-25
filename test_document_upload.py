#!/usr/bin/env python3
"""
Test Document Processing untuk EksporAI MVP
"""
from utils.document_processor import process_document_file
import os

def test_document_processing():
    print('🧪 TESTING DOCUMENT UPLOAD & PROCESSING')
    print('=' * 60)

    # Test dengan file teks yang baru dibuat
    test_file = 'test_umkm_data.txt'
    if os.path.exists(test_file):
        print(f'📄 Testing with: {test_file}')
        try:
            result = process_document_file(test_file)
            print('✅ Processing successful!')
            print()
            print('📋 EXTRACTED UMKM DATA:')
            print('-' * 40)

            # Group fields by category
            basic_info = {}
            financial_info = {}
            certifications = {}
            other_info = {}

            for key, value in result.items():
                if value:  # Only show non-empty values
                    if key in ['nama', 'alamat', 'nib', 'npwp']:
                        basic_info[key.upper()] = value
                    elif key in ['modal_usaha', 'omzet_bulanan', 'tahun_berdiri']:
                        financial_info[key.replace('_', ' ').title()] = value
                    elif 'sertifikat' in key.lower():
                        certifications[key.replace('_', ' ').title()] = value
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
                print('📜 CERTIFICATIONS:')
                for k, v in certifications.items():
                    print(f'  • {k}: {v}')
                print()

            if other_info:
                print('📊 OTHER INFORMATION:')
                for k, v in other_info.items():
                    print(f'  • {k}: {v}')

            print()
            print('🎯 EXTRACTION CONFIDENCE:')
            if 'confidence' in result:
                print(f'  • Overall: {result["confidence"]:.1%}')

        except Exception as e:
            print(f'❌ Error: {e}')
            import traceback
            traceback.print_exc()
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
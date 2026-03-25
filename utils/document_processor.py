# utils/document_processor.py
"""
Enhanced Document Processing dengan OCR + NLP
Ekstraksi otomatis data UMKM dari berbagai format dokumen
"""
import PyPDF2
import re
from typing import Dict, Optional
from PIL import Image
import io
import numpy as np

# NLP imports (dengan graceful fallback)
try:
    import spacy
    nlp = None
    try:
        nlp = spacy.load("id_core_news_sm")
    except:
        try:
            print("⚠️ Spacy ID model belum diinstall. Trying English model...")
            nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️ Spacy models tidak tersedia. Akan gunakan regex-only extraction.")
            nlp = None
except ImportError:
    print("⚠️ Spacy tidak tersedia (optional)")
    nlp = None

# OCR imports (dengan graceful fallback)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    print("⚠️ pytesseract tidak tersedia. OCR akan skip.")
    TESSERACT_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    print("⚠️ pdf2image tidak tersedia. Image extraction akan limited.")
    PDF2IMAGE_AVAILABLE = False


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from PDF file dengan dual approach:
    1. Text extraction (digital PDF)
    2. OCR (scanned image)
    
    Parameters:
    pdf_file: Uploaded file object dari Streamlit
    
    Returns:
    str: Extracted text
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        # Coba extract text dari setiap halaman
        for page_num in range(len(pdf_reader.pages)):
            try:
                page = pdf_reader.pages[page_num]
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text
            except Exception as e:
                print(f"⚠️ Error extracting text from page {page_num}: {e}")
                continue
        
        # Jika text extraction gagal atau kosong, gunakan OCR
        if not text.strip() and PDF2IMAGE_AVAILABLE and TESSERACT_AVAILABLE:
            pdf_file.seek(0)
            images = convert_from_bytes(pdf_file.read())
            for image in images:
                try:
                    ocr_text = pytesseract.image_to_string(image, lang='ind+eng')
                    if ocr_text:
                        text += ocr_text
                except Exception as e:
                    print(f"⚠️ OCR error: {e}")
        
        return text
    
    except Exception as e:
        print(f"❌ Error extracting PDF: {e}")
        return ""


def extract_text_from_image(image_file) -> str:
    """
    Extract text dari image file menggunakan OCR
    
    Parameters:
    image_file: Image file object
    
    Returns:
    str: Extracted text
    """
    if not TESSERACT_AVAILABLE:
        print("❌ Tesseract tidak tersedia")
        return ""
    
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image, lang='ind+eng')
        return text
    except Exception as e:
        print(f"❌ Error extracting text from image: {e}")
        return ""


def parse_umkm_data_from_text(text: str) -> Dict:
    """
    Parse UMKM data dari extracted text menggunakan regex + NLP
    
    Parameters:
    text (str): Extracted text dari document
    
    Returns:
    dict: Parsed UMKM data dengan confidence scores
    """
    data = {}
    
    # Regex patterns untuk common UMKM data fields
    patterns = {
        'nib': r'(?:NIB|Nomor\s+Induk\s+Berusaha)[:\s]*([0-9]{13,16})',
        'nama_usaha': r'(?:Nama\s+(?:Usaha|Perusahaan|Bisnis))[:\s]*([A-Za-z\s\-]+?)(?:\n|$)',
        'npwp': r'(?:NPWP)[:\s]*([0-9\.\-]{15,20})',
        'modal': r'(?:Modal\s+(?:Usaha|Awal|Kerja))[:\s]*Rp[\s\.]*([0-9,\.]+)',
        'omzet': r'(?:Omzet|Pendapatan|Penjualan)(?:\s+(?:Bulanan|Tahunan|Rata-rata))?[:\s]*Rp[\s\.]*([0-9,\.]+)',
        'tahun_berdiri': r'(?:Tahun\s+(?:Berdiri|Didirikan|Mulai))[:\s]*([0-9]{4})',
        'jumlah_karyawan': r'(?:Jumlah\s+(?:Karyawan|Tenaga\s+Kerja|Pegawai))[:\s]*([0-9]+)',
        'kapasitas': r'(?:Kapasitas\s+(?:Produksi|Produk))[:\s]*([0-9,\.]+)',
        'alamat': r'(?:Alamat|Lokasi)[:\s]*([A-Za-z0-9\s\-,\.]+?)(?:\n|$)',
    }
    
    # Extract field-field menggunakan regex
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            # Clean up values
            if field in ['modal', 'omzet', 'kapasitas']:
                value = _extract_number(value)
            data[field] = value
    
    # Extract certifications
    data['punya_sertifikat_halal'] = 1 if re.search(r'sertifikat\s+halal|halal\s+cert', text, re.IGNORECASE) else 0
    data['punya_sertifikat_bpom'] = 1 if re.search(r'sertifikat\s+bpom|bpom|izin\s+edar', text, re.IGNORECASE) else 0
    data['punya_nib'] = 1 if re.search(r'nib|nomor\s+induk\s+berusaha', text, re.IGNORECASE) else 0
    data['ekspor_sebelumnya'] = 1 if re.search(r'pernah\s+ekspor|sudah\s+export|pengalaman\s+export', text, re.IGNORECASE) else 0
    
    # NLP-based enhancement (jika Spacy tersedia)
    if nlp:
        doc = nlp(text[:5000])  # Process first 5000 chars untuk efficiency
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if 'nama_pemilik' not in data:
                    data['nama_pemilik'] = ent.text
            elif ent.label_ == "ORG" and 'nama_usaha' not in data:
                data['nama_usaha'] = ent.text
            elif ent.label_ == "GPE":
                if 'lokasi' not in data:
                    data['lokasi'] = ent.text
    
    # Add confidence scores
    confidence = {
        'nib_confidence': 0.95 if 'nib' in data else 0,
        'npwp_confidence': 0.95 if 'npwp' in data else 0,
        'modal_confidence': 0.90 if 'modal' in data else 0,
        'omzet_confidence': 0.85 if 'omzet' in data else 0,
        'overall_confidence': len(data) / len(patterns) if data else 0
    }
    
    data['extraction_confidence'] = confidence
    data['extraction_status'] = 'success' if confidence['overall_confidence'] > 0.5 else 'partial'
    
    return data


def _extract_number(text: str) -> float:
    """Extract numeric value dari string dengan format Rp"""
    text = text.replace('Rp', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(text)
    except:
        return 0


def validate_umkm_data(data: Dict) -> Dict:
    """
    Validate ekstracted UMKM data
    
    Returns:
    dict: Validation results dengan warnings
    """
    validation = {
        'is_valid': True,
        'warnings': [],
        'errors': []
    }
    
    # Check required fields
    required_fields = ['nib', 'nama_usaha', 'tahun_berdiri']
    for field in required_fields:
        if field not in data or not data[field]:
            validation['errors'].append(f"Required field '{field}' is missing")
            validation['is_valid'] = False
    
    # Check data sanity
    if 'tahun_berdiri' in data:
        try:
            tahun = int(data['tahun_berdiri'])
            if tahun < 1900 or tahun > 2026:
                validation['warnings'].append(f"Year {tahun} seems invalid")
        except:
            pass
    
    if 'omzet' in data and 'modal' in data:
        try:
            if float(data['omzet']) < float(data['modal']):
                validation['warnings'].append("Omzet shouldn't be less than modal")
        except:
            pass
    
    # Check extraction confidence
    confidence = data.get('extraction_confidence', {})
    if confidence.get('overall_confidence', 0) < 0.5:
        validation['warnings'].append("Extraction confidence is low. Please review manually.")
    
    return validation


def process_document_file(uploaded_file) -> Dict:
    """
    Main function untuk process uploaded document (PDF atau Image)
    
    Parameters:
    uploaded_file: Streamlit uploaded file
    
    Returns:
    dict: Processed UMKM data dengan validation results
    """
    file_type = uploaded_file.type
    
    # Determine file type dan extract accordingly
    if file_type == 'application/pdf':
        text = extract_text_from_pdf(uploaded_file)
    elif file_type.startswith('image/'):
        text = extract_text_from_image(uploaded_file)
    else:
        return {
            'status': 'error',
            'message': f'Unsupported file type: {file_type}',
            'data': {}
        }
    
    if not text:
        return {
            'status': 'error',
            'message': 'Failed to extract text from document',
            'data': {}
        }
    
    # Parse extracted text
    umkm_data = parse_umkm_data_from_text(text)
    
    # Validate parsed data
    validation = validate_umkm_data(umkm_data)
    
    return {
        'status': 'success' if validation['is_valid'] else 'partial',
        'message': 'Data extracted successfully' if validation['is_valid'] else 'Data extracted with warnings',
        'data': umkm_data,
        'validation': validation,
        'raw_text': text[:500]  # Store first 500 chars for reference
    }
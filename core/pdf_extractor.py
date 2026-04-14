import fitz  # PyMuPDF
import pdfplumber
import re
import io

def extract_text_from_pdf(file_object) -> str:
    """
    LinkedIn PDF'inden veya normal PDF'ten temiz metin çıkarır.
    Önce PyMuPDF dener, başarısız olursa pdfplumber kullanır.
    """
    # Streamlit UploadedFile objesi ise bytes al, değilse kendisi bytes veya IO
    if hasattr(file_object, 'read'):
        pdf_bytes = file_object.read()
    else:
        pdf_bytes = file_object
        
    try:
        # Yöntem 1: PyMuPDF (genellikle daha hızlı)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text("text"))
        
        raw_text = "\n".join(text_parts)
        
        # LinkedIn PDF'ine özel temizleme
        cleaned = clean_linkedin_text(raw_text)
        
        if len(cleaned.split()) < 20: # Test için bazen çok kısa olabilir
            raise ValueError("Çok az kelime çıkarıldı, pdfplumber deneniyor")
        
        return cleaned
    
    except Exception:
        # Yöntem 2: pdfplumber (tablo ve karmaşık düzenler için daha iyi)
        if hasattr(file_object, 'seek'):
            file_object.seek(0)
            io_obj = file_object
        else:
            io_obj = io.BytesIO(pdf_bytes)
            
        with pdfplumber.open(io_obj) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return clean_linkedin_text("\n".join(pages))


def clean_linkedin_text(text: str) -> str:
    """LinkedIn PDF'ine özgü gereksiz metinleri temizler."""
    if not text:
        return ""
    # Sayfa numaralarını kaldır
    text = re.sub(r'\n\d+\s*\n', '\n', text)
    # Ardışık boşlukları temizle
    text = re.sub(r'\n{3,}', '\n\n', text)
    # LinkedIn UI metinlerini kaldır
    patterns_to_remove = [
        r'Contact\s+Top\s+Skills',
        r'LinkedIn.*?Profile',
        r'www\.linkedin\.com',
        r'Page \d+ of \d+'
    ]
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text.strip()

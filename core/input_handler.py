from core.pdf_extractor import extract_text_from_pdf

def get_combined_text(uploaded_file, manual_text: str) -> str:
    combined = ""
    if uploaded_file is not None:
        combined += "=== PDF İÇERİĞİ ===\n"
        # Reset file pointer if read before
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)
        combined += extract_text_from_pdf(uploaded_file) + "\n\n"
        
    if manual_text and manual_text.strip() != "":
        combined += "=== EK BİLGİ/MANUEL METİN ===\n"
        combined += manual_text.strip() + "\n"
        
    return combined

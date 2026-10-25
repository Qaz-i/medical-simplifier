import fitz  # PyMuPDF
import easyocr
import tempfile, os
from PIL import Image
import numpy as np

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF. Uses PyMuPDF first, falls back to EasyOCR for scanned PDFs."""
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    
    text = ""
    try:
        doc = fitz.open(tmp_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    finally:
        os.unlink(tmp_path)
    
    # If no text found (scanned PDF), use OCR
    if len(text.strip()) < 50:
        text = ocr_from_pdf(uploaded_file)
    
    return text.strip()


def ocr_from_pdf(uploaded_file):
    """Use EasyOCR on scanned PDFs by converting pages to images first."""
    uploaded_file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    
    reader = easyocr.Reader(['en'], gpu=False)
    all_text = []
    
    try:
        doc = fitz.open(tmp_path)
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8)
            img_array = img_array.reshape(pix.height, pix.width, pix.n)
            results = reader.readtext(img_array, detail=0)
            all_text.extend(results)
        doc.close()
    finally:
        os.unlink(tmp_path)
    
    return "\n".join(all_text)

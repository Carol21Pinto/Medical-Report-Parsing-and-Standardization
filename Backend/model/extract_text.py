import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from docx import Document
import PyPDF2

def extract_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def extract_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_from_pdf(file_path):
    text = ""
    try:
        reader = PyPDF2.PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except:
        pass

    if text.strip():
        return text

    # OCR fallback
    images = convert_from_path(file_path)
    ocr_text = ""
    for img in images:
        ocr_text += pytesseract.image_to_string(img) + "\n"
    return ocr_text

def extract_from_image(file_path):
    img = Image.open(file_path)
    return pytesseract.image_to_string(img)

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        return extract_from_txt(file_path)
    elif ext == ".docx":
        return extract_from_docx(file_path)
    elif ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        return extract_from_image(file_path)
    else:
        return ""

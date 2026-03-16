import PyPDF2
import sys
import os

pdf_path = 'Whatsapp Scan 10 March 2026 at 15.54.23.pdf'
try:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        print("--- EXTRACTED TEXT ---")
        print(text)
except Exception as e:
    print(f"Error reading PDF: {e}")

try:
    import fitz # PyMuPDF
    res = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            res += page.get_text()
    print("--- PyMuPDF EXTRACTED TEXT ---")
    print(res)
except Exception as e:
    print(f"PyMuPDF Error: {e}")

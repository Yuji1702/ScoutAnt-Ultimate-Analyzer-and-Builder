import fitz # PyMuPDF
import sys
import os

pdf_path = 'Whatsapp Scan 10 March 2026 at 15.54.23.pdf'
try:
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        image_list = page.get_images(full=True)
        if image_list:
            for j, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_name = f"page_{i}_img_{j}.{image_ext}"
                with open(image_name, "wb") as f:
                    f.write(image_bytes)
                print(f"Extracted {image_name}")
        else:
            print(f"No images found on page {i}")
except Exception as e:
    print(f"Error: {e}")

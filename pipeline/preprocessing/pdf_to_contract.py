from pathlib import Path
import fitz 


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from PDF using PyMuPDF for better layout preservation.
    """
    doc = fitz.open(pdf_path)
    text_blocks = []

    for page in doc:
        page_text = page.get_text("text")
        if page_text:
            text_blocks.append(page_text)

    doc.close()
    return "\n".join(text_blocks)

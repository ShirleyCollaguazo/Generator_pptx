from pathlib import Path
import PyPDF2


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract raw text from a PDF file.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = []

    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

    return "\n".join(text).strip()

from pipeline.preprocessing.pdf_to_contract import extract_text_from_pdf
from pathlib import Path

text = extract_text_from_pdf(Path("data/Computer.pdf"))

print("TOTAL CHARS:", len(text))
print("\n===== INICIO =====\n")
print(text[:2000])
print("\n===== MEDIO =====\n")
print(text[len(text)//2 : len(text)//2 + 2000])
print("\n===== FINAL =====\n")
print(text[-2000:])

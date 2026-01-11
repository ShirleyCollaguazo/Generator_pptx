from pathlib import Path
from pipeline.preprocessing.macro_section_splitter import MacroSectionSplitter
from pipeline.preprocessing.pdf_to_contract import extract_text_from_pdf

PDF_PATH = Path("data/sample.pdf")

text = extract_text_from_pdf(PDF_PATH)

splitter = MacroSectionSplitter(
    tokenizer_name_or_path="google/long-t5-tglobal-base"
)

sections = splitter.split(text)

print(f"Total macro-secciones: {len(sections)}")
for sec in sections:
    print(sec["section_id"], "->", len(sec["text"].split()), "palabras")

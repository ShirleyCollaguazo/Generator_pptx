from pathlib import Path

from pipeline.contracts.contract_reset import reset_contract
from pipeline.preprocessing.pdf_to_contract import extract_text_from_pdf
from pipeline.preprocessing.macrosection_splitter import MacroSectionSplitter
from pipeline.inference.title_to_contract import write_titles_to_contract
from pipeline.inference.idea_to_contract import write_ideas_to_contract
from pipeline.mapping.slice_mapper import map_contract_to_slices
from pipeline.render.pptx_renderer import render_pptx_from_contract


PDF_PATH = Path("data/example.pdf")
CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")
TEMPLATE_PATH = Path("assets/templates/base_template.pptx")
OUTPUT_PATH = Path("outputs/result_macro.pptx")

# ─────────────────────────────
# 0️⃣ RESET CONTRACT (CLAVE)
# ─────────────────────────────
reset_contract(CONTRACT_PATH)

# 1️⃣ Extraer texto
full_text = extract_text_from_pdf(PDF_PATH)

# 2️⃣ Macro-secciones
splitter = MacroSectionSplitter(max_words=1800)
macrosections = splitter.split(full_text)

print(f"[INFO] Macrosecciones generadas: {len(macrosections)}")

# 3️⃣ Procesar macro-secciones
for idx, section_text in enumerate(macrosections):
    section_id = f"SEC_{idx}"

    write_titles_to_contract(
        contract_path=CONTRACT_PATH,
        section_id=section_id,
        text=section_text,
        base_model_name="t5-base",
        adapter_path="models/title_model"
    )

    write_ideas_to_contract(
        contract_path=CONTRACT_PATH,
        section_id=section_id,
        text=section_text,
        idea_model_path="models/idea_model"
    )

# 4️⃣ Mapping (una sola vez)
map_contract_to_slices(CONTRACT_PATH)

# 5️⃣ Render
render_pptx_from_contract(
    contract_path=CONTRACT_PATH,
    template_path=TEMPLATE_PATH,
    output_path=OUTPUT_PATH
)

print("[OK] PPTX generado desde PDF con macro-secciones")

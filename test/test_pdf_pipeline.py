from pathlib import Path

from pipeline.preprocessing.pdf_to_contract import extract_text_from_pdf
from pipeline.inference.title_to_contract import write_titles_to_contract
from pipeline.inference.idea_to_contract import write_ideas_to_contract
from pipeline.mapping.slice_mapper import map_contract_to_slices
from pipeline.render.pptx_renderer import render_pptx_from_contract


PDF_PATH = Path("data/sample.pdf")
CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")
TEMPLATE_PATH = Path("assets/templates/base_template.pptx")
OUTPUT_PATH = Path("outputs/result_from_pdf.pptx")


# 1️⃣ Extract text
text = extract_text_from_pdf(PDF_PATH)

# 2️⃣ Titles → contract
write_titles_to_contract(
    contract_path=CONTRACT_PATH,
    text=text,
    base_model_name="t5-base",
    adapter_path="models/title_model"
)

# 3️⃣ Ideas → contract
write_ideas_to_contract(
    contract_path=CONTRACT_PATH,
    text=text,
    idea_model_path="models/idea_model"
)




# 4️⃣ Map slices + bullets inteligentes
map_contract_to_slices(CONTRACT_PATH)

# 5️⃣ Render PPTX
render_pptx_from_contract(
    contract_path=CONTRACT_PATH,
    template_path=TEMPLATE_PATH,
    output_path=OUTPUT_PATH
)

print("✅ PPTX generado desde PDF correctamente.")

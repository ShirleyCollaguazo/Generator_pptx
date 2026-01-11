from pathlib import Path
from pipeline.render.pptx_renderer import render_pptx_from_contract

CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")
TEMPLATE_PATH = Path("assets/templates/base_template.pptx")
OUTPUT_PATH = Path("outputs/result.pptx")

render_pptx_from_contract(
    contract_path=CONTRACT_PATH,
    template_path=TEMPLATE_PATH,
    output_path=OUTPUT_PATH
)

print("PPTX generado correctamente.")



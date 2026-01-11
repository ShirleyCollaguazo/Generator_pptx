from pathlib import Path

from pipeline.contracts.contract_reset import reset_contract
from pipeline.preprocessing.pdf_to_contract import extract_text_from_pdf
from pipeline.preprocessing.macrosection_splitter import MacroSectionSplitter
from pipeline.inference.title_to_contract import write_titles_to_contract
from pipeline.inference.idea_to_contract import write_ideas_to_contract
from pipeline.mapping.slice_mapper import map_contract_to_slices
from pipeline.render.pptx_renderer import render_pptx_from_contract


# ─────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────
PDF_PATH = Path("data/sample.pdf")
CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")
TEMPLATE_PATH = Path("assets/templates/base_template.pptx")
OUTPUT_PATH = Path("outputs/result_final.pptx")


def main() -> None:
    # ─────────────────────────────
    # 0️⃣ RESET CONTRACT (OBLIGATORIO)
    # ─────────────────────────────
    reset_contract(CONTRACT_PATH)

    # ─────────────────────────────
    # 1️⃣ EXTRAER TEXTO DEL PDF
    # ─────────────────────────────
    full_text = extract_text_from_pdf(PDF_PATH)
    print(f"[INFO] Texto extraído (chars): {len(full_text)}")

    # ─────────────────────────────
    # 2️⃣ DIVIDIR EN MACROSECCIONES
    # ─────────────────────────────
    splitter = MacroSectionSplitter(max_words=1800)
    macrosections = splitter.split(full_text)

    print(f"[INFO] Macrosecciones generadas: {len(macrosections)}")

    # ─────────────────────────────
    # 3️⃣ PROCESAR CADA MACROSECCIÓN
    # ─────────────────────────────
    for sec in macrosections:
        section_id = sec["section_id"]
        section_text = sec["text"]

        print(f"\n🧩 Procesando {section_id}")
        print(f"   - chars: {len(section_text)}")

        # 3.1 TÍTULOS
        write_titles_to_contract(
            contract_path=CONTRACT_PATH,
            section_id=section_id,
            text=section_text,
            base_model_name="t5-base",
            adapter_path="models/title_model"
        )

        # 3.2 IDEAS
        write_ideas_to_contract(
            contract_path=CONTRACT_PATH,
            section_id=section_id,
            text=section_text,
            idea_model_path="models/idea_model"
        )

    # ─────────────────────────────
    # 4️⃣ MAPEO A SLICES (UNA SOLA VEZ)
    # ─────────────────────────────
    map_contract_to_slices(CONTRACT_PATH)
    print("[INFO] Mapping a slices completado")

    # ─────────────────────────────
    # 5️⃣ RENDER FINAL A PPTX
    # ─────────────────────────────
    render_pptx_from_contract(
        contract_path=CONTRACT_PATH,
        template_path=TEMPLATE_PATH,
        output_path=OUTPUT_PATH
    )

    print(f"[OK] PPTX generado correctamente → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

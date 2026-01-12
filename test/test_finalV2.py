from pathlib import Path

from pipeline.contracts.contract_reset import reset_contract
from pipeline.preprocessing.pdf_to_contract import extract_text_from_pdf
from pipeline.preprocessing.macrosection_splitter import MacroSectionSplitter
from pipeline.inference.title_to_contract import write_titles_to_contract
from pipeline.inference.idea_to_contract import write_ideas_to_contract
from pipeline.mapping.slice_mapper import map_contract_to_slices
from pipeline.render.pptx_renderer import render_pptx_from_contract
from pipeline.translation.language_detector import detect_language
from pipeline.translation.translator import DeepLTranslator
from pipeline.contracts.contract_io import load_contract, save_contract


# ─────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────
PDF_PATH = Path("data/EjemploEspaniol.pdf")
CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")
TEMPLATE_PATH = Path("assets/templates/base_template.pptx")
OUTPUT_PATH = Path("outputs/result_finalv2T.pptx")


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
    #  DETECTAR IDIOMA Y TRADUCIR A INGLÉS (SI APLICA)
    # ─────────────────────────────
    detected_lang = detect_language(full_text)
    print(f"[INFO] Idioma detectado: {detected_lang}")

    translator = DeepLTranslator()

    if detected_lang == "es":
        print("[INFO] Traduciendo texto de entrada ES → EN ...")
        full_text = translator.translate(full_text, "ES", "EN")
        print(f"[INFO] Texto traducido a EN (chars): {len(full_text)}")
    else:
        print("[INFO] No se requiere traducción de entrada")


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
    # TRADUCIR SALIDA EN → ES (ANTES DEL RENDER)
    # ─────────────────────────────
    print("[INFO] Traduciendo salida EN → ES ...")

    translator = DeepLTranslator()

    # Cargar contrato desde JSON
    contract = load_contract(CONTRACT_PATH)

    # Traducir títulos del outline
    for item in contract.get("outline", []):
        if item.get("title_text"):
            item["title_text"] = translator.translate(
                item["title_text"], "EN", "ES"
            )

    # Traducir ideas
    for idea in contract.get("ideas", []):
        if idea.get("text"):
            idea["text"] = translator.translate(
                idea["text"], "EN", "ES"
            )

    # Traducir slides
    for slide in contract.get("slides", []):
        # Título del slide
        if slide.get("title_text"):
            slide["title_text"] = translator.translate(
                slide["title_text"], "EN", "ES"
            )

        # Contenido
        content = slide.get("content", {})
        if content.get("content_type") == "paragraph":
            content["text"] = translator.translate(
                content["text"], "EN", "ES"
            )
        elif content.get("content_type") == "bullets":
            content["bullets"] = [
                translator.translate(b, "EN", "ES")
                for b in content.get("bullets", [])
            ]

    # Guardar contrato traducido
    save_contract(contract, CONTRACT_PATH)

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

from pathlib import Path
from pipeline.preprocessing.academic_text_cleaner import clean_academic_text
from pipeline.contracts.contract_reset import reset_contract
from pipeline.preprocessing.macrosection_splitter import MacroSectionSplitter
from pipeline.inference.title_to_contract import write_titles_to_contract
from pipeline.inference.idea_to_contract import write_ideas_to_contract
from pipeline.mapping.slice_mapper import map_contract_to_slices
from pipeline.render.pptx_renderer import render_pptx_from_contract

from pipeline.translation.language_detector import detect_language
from pipeline.translation.translator import DeepLTranslator
from pipeline.contracts.contract_io import load_contract, save_contract


# Rutas base 
CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")
TEMPLATE_PATH = Path("assets/templates/base_template.pptx")


def run_pipeline(input_text: str, output_path: str | Path) -> Path:
    """
    Ejecuta el pipeline completo (con traducción bidireccional)
    usando TEXTO PLANO como entrada y genera un PPTX.

    Retorna: Path del PPTX generado.
    """
    output_path = Path(output_path)

    # Asegurar carpeta outputs
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # RESET CONTRACT
    reset_contract(CONTRACT_PATH)

    # TEXTO DE ENTRADA (YA NO VIENE DE PDF)
    cleaned = clean_academic_text(input_text)

    document_title = cleaned["title"]   # ← se conserva (no rompe nada)
    full_text = cleaned["body"]

    # DETECTAR IDIOMA Y TRADUCIR A INGLÉS
    detected_lang = detect_language(full_text)
    translator = DeepLTranslator()

    if detected_lang == "es":
        full_text = translator.translate(full_text, "ES", "EN")

    # DIVIDIR EN MACROSECCIONES
    splitter = MacroSectionSplitter(max_words=1800)
    macrosections = splitter.split(full_text)

    # PROCESAR CADA MACROSECCIÓN
    for sec in macrosections:
        section_id = sec["section_id"]
        section_text = sec["text"]

        # 1. TÍTULOS
        write_titles_to_contract(
            contract_path=CONTRACT_PATH,
            section_id=section_id,
            text=section_text
        )

        # 2. IDEAS
        write_ideas_to_contract(
            contract_path=CONTRACT_PATH,
            section_id=section_id,
            text=section_text
        )

    # MAPEO A SLICES (UNA SOLA VEZ)
    map_contract_to_slices(CONTRACT_PATH)

    # TRADUCIR SALIDA EN → ES (ANTES DEL RENDER) SI EL INPUT ERA ES
    if detected_lang == "es":
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
            if slide.get("title_text"):
                slide["title_text"] = translator.translate(
                    slide["title_text"], "EN", "ES"
                )

            content = slide.get("content", {})
            if content.get("content_type") == "paragraph":
                content["text"] = translator.translate(
                    content.get("text", ""), "EN", "ES"
                )
            elif content.get("content_type") == "bullets":
                content["bullets"] = [
                    translator.translate(b, "EN", "ES")
                    for b in content.get("bullets", [])
                ]

        save_contract(contract, CONTRACT_PATH)

    # RENDER FINAL A PPTX
    render_pptx_from_contract(
        contract_path=CONTRACT_PATH,
        template_path=TEMPLATE_PATH,
        output_path=output_path
    )

    return output_path
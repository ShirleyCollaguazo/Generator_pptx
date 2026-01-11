# pipeline/inference/macrosection_pipeline.py

from pathlib import Path
from typing import List, Dict

from pipeline.preprocessing.macro_section_splitter import MacroSectionSplitter
from pipeline.inference.title_generator import TitleGenerator
from pipeline.inference.idea_generator import IdeaGenerator
from pipeline.contracts.contract_io import load_contract, save_contract


def process_text_with_macrosections(
    contract_path: Path,
    full_text: str,
    title_model_base: str,
    title_adapter_path: str,
    idea_model_path: str
) -> None:
    """
    Procesa un texto largo usando macrosecciones y llena el contrato
    con títulos e ideas alineadas pedagógicamente.
    """

    # 1️⃣ Cargar contrato base
    contract = load_contract(contract_path)

    # 2️⃣ Dividir texto en macrosecciones coherentes
    macrosections: List[Dict] = MacroSectionSplitter(full_text)

    # 3️⃣ Inicializar modelos
    title_generator = TitleGenerator(
        base_model_name=title_model_base,
        adapter_path=title_adapter_path
    )

    idea_generator = IdeaGenerator(
        model_path=idea_model_path
    )

    outline = []
    ideas = []

    title_counter = 0

    # 4️⃣ Procesar cada macrosección
    for section in macrosections:
        section_id = section["section_id"]
        section_text = section["raw_text"]

        # ── 4.1 Generar título ──
        titles = title_generator.generate_titles(section_text)
        title_text = titles[0] if titles else "Sección"

        title_id = f"T{title_counter}"

        outline.append({
            "title_id": title_id,
            "title_text": title_text,
            "source_section_id": section_id
        })

        # ── 4.2 Generar ideas ──
        section_ideas = idea_generator.generate_ideas(section_text)

        for idx, idea_text in enumerate(section_ideas):
            if not idea_text.strip():
                continue

            ideas.append({
                "idea_id": f"{title_id}_I{idx+1}",
                "title_id": title_id,
                "text": idea_text.strip()
            })

        title_counter += 1

    # 5️⃣ Escribir en el contrato
    contract["outline"] = outline
    contract["ideas"] = ideas

    # 6️⃣ Guardar contrato
    save_contract(contract, contract_path)

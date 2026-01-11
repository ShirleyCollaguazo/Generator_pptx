from pathlib import Path
from typing import List, Dict

from pipeline.contracts.contract_io import load_contract, save_contract
from pipeline.inference.idea_generator import IdeaGenerator


def write_ideas_to_contract(
    contract_path: Path,
    section_id: str,
    text: str,
    idea_model_path: str
) -> None:
    """
    Genera UNA o MÁS ideas por macrosección y las guarda en el contrato.
    """

    contract = load_contract(contract_path)

    generator = IdeaGenerator(model_dir=idea_model_path)

    existing_ideas = contract.get("ideas", [])
    outline = contract.get("outline", [])

    # Títulos asociados a esta macrosección
    section_titles = [
        o for o in outline if o["source_section_id"] == section_id
    ]

    # Generar ideas (LISTA)
    ideas_generated = generator.generate_ideas(text)

    for outline_item in section_titles:
        title_id = outline_item["title_id"]

        for idx, idea in enumerate(ideas_generated, start=1):
            idea_text = idea.get("idea_text", "").strip()

            if not idea_text:
                continue

            existing_ideas.append({
                "idea_id": f"{title_id}_I{idx}",
                "title_id": title_id,
                "section_id": section_id,
                "text": idea_text
            })

    contract["ideas"] = existing_ideas
    save_contract(contract, contract_path)

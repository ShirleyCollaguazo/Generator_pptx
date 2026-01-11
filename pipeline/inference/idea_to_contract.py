from pathlib import Path
from typing import Dict, List

from pipeline.contracts.contract_io import load_contract, save_contract
from pipeline.inference.idea_generator import IdeaGenerator


def write_ideas_to_contract(
    contract_path: Path,
    section_id: str,
    text: str,
    idea_model_path: str
) -> None:

    contract = load_contract(contract_path)

    generator = IdeaGenerator(model_dir=idea_model_path)

    existing_ideas = contract.get("ideas", [])
    outline = contract.get("outline", [])

    # Solo títulos de ESTA macro-sección
    section_titles = [
        o for o in outline if o["source_section_id"] == section_id
    ]

    for outline_item in section_titles:
        title_id = outline_item["title_id"]
        result = generator.generate_ideas(text)

        for i in [1, 2]:
            idea_text = result.get(f"idea_{i}", "").strip()
            if idea_text:
                existing_ideas.append({
                    "idea_id": f"{title_id}_I{i}",
                    "title_id": title_id,
                    "section_id": section_id,   # ✅ CLAVE
                    "text": idea_text
                })

    contract["ideas"] = existing_ideas
    save_contract(contract, contract_path)


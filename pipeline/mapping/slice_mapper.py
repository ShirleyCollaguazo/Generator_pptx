from pathlib import Path
from typing import List, Dict

from pipeline.contracts.contract_io import load_contract, save_contract
from pipeline.mapping.content_mapper import map_text_to_content


def map_contract_to_slices(contract_path: Path) -> None:
    """
    1 macro-section = 1 content slide
    """

    contract = load_contract(contract_path)

    outline = contract.get("outline", [])
    ideas = contract.get("ideas", [])

    slides: List[Dict] = []
    slide_index = 0

    # ───── TITLE SLIDE (solo uno) ─────
    if outline:
        slides.append({
            "slide_id": f"S{slide_index}",
            "slide_type": "title",
            "title_text": outline[0]["title_text"]
        })
        slide_index += 1

    # ───── CONTENT SLIDES ─────
    for idea in ideas:
        section_id = idea.get("section_id")
        if not section_id:
            continue  # ignora ideas antiguas


        title_text = next(
            (o["title_text"] for o in outline if o["source_section_id"] == section_id),
            "Contenido"
        )

        slides.append({
            "slide_id": f"S{slide_index}",
            "slide_type": "content",
            "title_text": title_text,
            "content": map_text_to_content(idea["text"])
        })

        slide_index += 1

    contract["slides"] = slides
    save_contract(contract, contract_path)

from pathlib import Path
from typing import List, Dict

from pipeline.contracts.contract_io import load_contract, save_contract
from pipeline.mapping.content_mapper import map_text_to_content


MAX_BULLETS_PER_SLICE = 3


def map_contract_to_slices(contract_path: Path) -> None:
    """
    Maps ideas to one or more content slides depending on overflow rules.
    """

    contract = load_contract(contract_path)

    outline = contract.get("outline", [])
    ideas = contract.get("ideas", [])

    slides: List[Dict] = []
    slide_index = 0

    # ───── TITLE SLIDE ─────
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
            continue

        title_text = next(
            (o["title_text"] for o in outline if o["source_section_id"] == section_id),
            "Contenido"
        )

        content = map_text_to_content(idea["text"])

        # ───── CASE 1: Paragraph or non-overflow bullets ─────
        if not content.get("overflow", False):
            slides.append({
                "slide_id": f"S{slide_index}",
                "slide_type": "content",
                "title_text": title_text,
                "content": content
            })
            slide_index += 1
            continue

        # ───── CASE 2: Overflow → split into multiple slides ─────
        bullets = content.get("bullets", [])
        bullet_chunks = _chunk_bullets(bullets, MAX_BULLETS_PER_SLICE)

        for chunk in bullet_chunks:
            slides.append({
                "slide_id": f"S{slide_index}",
                "slide_type": "content",
                "title_text": title_text,
                "content": {
                    "content_type": "bullets",
                    "bullets": chunk,
                    "overflow": False
                }
            })
            slide_index += 1

    contract["slides"] = slides
    save_contract(contract, contract_path)


def _chunk_bullets(bullets: List[str], max_per_chunk: int) -> List[List[str]]:
    """
    Splits a list of bullets into chunks of size <= max_per_chunk.
    """
    return [
        bullets[i:i + max_per_chunk]
        for i in range(0, len(bullets), max_per_chunk)
    ]

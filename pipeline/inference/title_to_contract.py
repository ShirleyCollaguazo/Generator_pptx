from pathlib import Path
from pipeline.contracts.contract_io import load_contract, save_contract
from pipeline.inference.title_generator import TitleGenerator


def write_titles_to_contract(
    contract_path: Path,
    section_id: str,
    text: str,
    base_model_name: str | None = None,
    adapter_path: str | None = None
):

    contract = load_contract(contract_path)

    generator = TitleGenerator(
    base_model_name=base_model_name,
    adapter_path=adapter_path
    )
    
    titles = generator.generate_titles(text)

    titles = [
        t.strip()
        for t in titles
        if t.strip().lower() not in {"true", "false", "yes", "no"}
    ]

    if not titles:
        titles = ["Título generado automáticamente"]

    outline = contract.get("outline", [])
    base_index = len(outline)

    for idx, title in enumerate(titles):
        outline.append({
            "title_id": f"T{base_index + idx}",
            "title_text": title,
            "source_section_id": section_id  
        })

    contract["outline"] = outline
    save_contract(contract, contract_path)


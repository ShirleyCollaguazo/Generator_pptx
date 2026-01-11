from pathlib import Path
import json


def reset_contract(contract_path: Path) -> None:
    """
    Reset the slide contract to a clean initial state.
    """

    empty_contract = {
        "outline": [],
        "ideas": [],
        "slides": []
    }

    with open(contract_path, "w", encoding="utf-8") as f:
        json.dump(empty_contract, f, indent=2, ensure_ascii=False)

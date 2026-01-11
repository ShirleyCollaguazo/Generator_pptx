# pipeline/contracts/contract_io.py

import json
from pathlib import Path
from typing import Dict


def load_contract(contract_path: Path) -> Dict:
    """
    Load the slide contract JSON from disk.
    """
    if not contract_path.exists():
        raise FileNotFoundError(f"Contract file not found: {contract_path}")

    with contract_path.open("r", encoding="utf-8") as f:
        contract = json.load(f)

    return contract


def save_contract(contract: Dict, contract_path: Path) -> None:
    """
    Save the slide contract JSON back to disk.
    """
    with contract_path.open("w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2, ensure_ascii=False)

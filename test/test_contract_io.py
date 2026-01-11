from pathlib import Path
from pipeline.contracts.contract_io import load_contract, save_contract

contract_path = Path("pipeline/contracts/slide_contract_v1.json")

contract = load_contract(contract_path)
print("Contrato cargado OK")

save_contract(contract, contract_path)
print("Contrato guardado OK")

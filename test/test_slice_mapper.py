from pathlib import Path
from pipeline.mapping.slice_mapper import map_contract_to_slices

CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")

map_contract_to_slices(CONTRACT_PATH)

print("Slices generados correctamente.")

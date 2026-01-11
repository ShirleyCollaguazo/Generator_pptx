from pathlib import Path
from pipeline.inference.idea_to_contract import write_ideas_to_contract

CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")
MODEL_PATH = "models/idea_model"

TEXT = """
Animals carry out the following essential functions: feeding, respiration, circulation, excretion, response, movement and reproduction.

Feeding: Most animals cannot absorb food; they ingest it. Animals have evolved in various ways to feed themselves. Phagocytosis is the predominant or unique feeding mechanism in sponges, ctenophores, cnidarians and a subset of bilateral animals.

Respiration: Whether they live in water or on land, all animals breathe; this means they can take in oxygen and release carbon dioxide.
"""

write_ideas_to_contract(
    contract_path=CONTRACT_PATH,
    text=TEXT,
    idea_model_path=MODEL_PATH
)

print("Ideas escritas en el contrato correctamente.")

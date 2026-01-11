from pathlib import Path

from pipeline.contracts.contract_reset import reset_contract
from pipeline.preprocessing.pdf_to_contract import extract_text_from_pdf
from pipeline.preprocessing.macrosection_splitter import MacroSectionSplitter
from pipeline.inference.idea_generator import IdeaGenerator


# ─────────────────────────────
# CONFIG
# ─────────────────────────────
PDF_PATH = Path("data/paper.pdf")
CONTRACT_PATH = Path("pipeline/contracts/slide_contract_v1.json")

IDEA_MODEL_PATH = "models/idea_model"


# ─────────────────────────────
# 0️⃣ RESET CONTRACT
# ─────────────────────────────
reset_contract(CONTRACT_PATH)


# ─────────────────────────────
# 1️⃣ Extraer texto del PDF
# ─────────────────────────────
full_text = extract_text_from_pdf(PDF_PATH)


# ─────────────────────────────
# 2️⃣ Macrosecciones coherentes
# ─────────────────────────────
splitter = MacroSectionSplitter(max_words=1800)
macrosections = splitter.split(full_text)

print(f"\n[INFO] Macrosecciones generadas: {len(macrosections)}\n")


# ─────────────────────────────
# 3️⃣ Inicializar generador de ideas
# ─────────────────────────────
idea_generator = IdeaGenerator(
    model_dir=IDEA_MODEL_PATH
)


# ─────────────────────────────
# 4️⃣ DEBUG CONTROLADO POR MACROSECCIÓN
# ─────────────────────────────
for sec in macrosections:
    section_id = sec["section_id"]
    section_text = sec["text"]

    print("=" * 80)
    print(f"🧩 {section_id}")
    print("-" * 80)

    print(f"Total chars en macrosección: {len(section_text)}")
    print("\n--- INICIO ---\n")
    print(section_text[:800])
    print("\n--- FINAL ---\n")
    print(section_text[-800:])

    print("\n💡 Idea generada:\n")

    ideas = idea_generator.generate_ideas(section_text)
    print(f"Ideas generadas: {len(ideas)}")

    for i, idea in enumerate(ideas, start=1):
        print(f"\nIdea {i}:\n")
        print(idea["idea_text"][:500])


print("\n[OK] Test de macrosecciones + ideas finalizado")

from dotenv import load_dotenv
load_dotenv()

from pipeline.inference.idea_generator import IdeaGenerator
from pipeline.inference.title_generator import TitleGenerator

print("🔹 Cargando IdeaGenerator desde Hugging Face...")
idea_gen = IdeaGenerator()
print("✅ IdeaGenerator OK")

print("🔹 Cargando TitleGenerator (LoRA) desde Hugging Face...")
title_gen = TitleGenerator()
print("✅ TitleGenerator OK")

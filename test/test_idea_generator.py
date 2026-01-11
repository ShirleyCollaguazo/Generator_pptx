from pipeline.inference.idea_generator import IdeaGenerator

MODEL_DIR = "models/idea_model"

text = """
Animals carry out the following essential functions: feeding, respiration, circulation, excretion, response, movement and reproduction.
        
Feeding: Most animals cannot absorb food; they ingest it. Animals have evolved in various ways to feed themselves. Phagocytosis is the predominant or unique feeding mechanism in sponges, ctenophores, cnidarians and a subset of bilateral animals.
        
Respiration: Whether they live in water or on land, all animals breathe; this means they can take in oxygen and release carbon dioxide. Thanks to their very simple bodies and thin walls, some animals use the diffusion of these substances through the skin. However, most animals have evolved complex tissues and organ systems for respiration.
        
Circulation: Many small aquatic animals, such as some worms, use only diffusion to transport oxygen and nutrient molecules to all their cells, and collect waste products from them. Diffusion is sufficient because these animals are only a few cells thick. However, larger animals have some kind of circulatory system to move substances inside their bodies.
"""

generator = IdeaGenerator(model_dir=MODEL_DIR)
ideas = generator.generate_ideas(text)

print("IDEAS GENERADAS:")
print("Idea 1:", ideas.get("idea_1", "").strip())
print("Idea 2:", ideas.get("idea_2", "").strip())

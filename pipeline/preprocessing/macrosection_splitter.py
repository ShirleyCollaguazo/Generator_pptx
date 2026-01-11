from typing import List
import math


class MacroSectionSplitter:
    """
    Divide texto largo en macro-secciones didácticas
    respetando límite de tokens del modelo de ideas.
    """

    def __init__(self, max_words: int = 1800):
        # usamos palabras ≈ tokens (seguro)
        self.max_words = max_words

    def split(self, text: str) -> List[str]:
        words = text.split()
        total_words = len(words)

        if total_words <= self.max_words:
            return [text]

        num_sections = math.ceil(total_words / self.max_words)

        sections = []
        for i in range(num_sections):
            start = i * self.max_words
            end = start + self.max_words
            chunk_words = words[start:end]
            sections.append(" ".join(chunk_words))

        return sections

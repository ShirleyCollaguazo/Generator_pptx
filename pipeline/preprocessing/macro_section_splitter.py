from typing import List, Dict
from transformers import AutoTokenizer


class MacroSectionSplitter:
    """
    Divide texto largo en macro-secciones basadas en tokens,
    respetando el límite del modelo de ideas.
    """

    def __init__(
        self,
        tokenizer_name_or_path: str,
        max_tokens: int = 1800,
        overlap: int = 150
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path)
        self.max_tokens = max_tokens
        self.overlap = overlap

    def split(self, text: str) -> List[Dict]:
        """
        Divide el texto en macro-secciones.
        """

        tokens = self.tokenizer.encode(text, add_special_tokens=False)

        sections = []
        start = 0
        section_index = 0

        while start < len(tokens):
            end = start + self.max_tokens
            chunk_tokens = tokens[start:end]

            chunk_text = self.tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True
            )

            sections.append({
                "section_id": f"SEC_{section_index}",
                "text": chunk_text.strip()
            })

            section_index += 1

            # avanzar con overlap
            start += self.max_tokens - self.overlap

        return sections

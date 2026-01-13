import re
from typing import List, Dict

MACRO_TOPIC_PATTERNS = [
    r'^computers classification',
    r'^data,\s*information\s*and\s*knowledge',
    r'^characteristics\s+of\s+computer',
    r'^computer\s+viruses',
]

MACRO_TOPIC_REGEX = re.compile(
    "|".join(MACRO_TOPIC_PATTERNS),
    re.IGNORECASE
)


class MacroSectionSplitter:
    """
    Divide el texto en macrosecciones por CAMBIO DE MACRO-TEMA REAL,
    manteniendo coherencia semántica y sin perder información.
    """

    def __init__(self, max_words: int = 1800):
        self.max_words = max_words

    def split(self, text: str) -> List[Dict]:
        paragraphs = self._normalize_paragraphs(text)

        sections: List[Dict] = []
        buffer: List[str] = []
        word_count = 0
        section_index = 1

        for para in paragraphs:
            para_words = len(para.split())
            is_new_macro_topic = bool(MACRO_TOPIC_REGEX.match(para.strip()))

            # Si aparece un NUEVO macro-tema y ya hay contenido acumulado,
            # cerramos la macrosección actual
            if is_new_macro_topic and buffer:
                sections.append({
                    "section_id": f"SEC_{section_index}",
                    "text": "\n\n".join(buffer).strip()
                })
                section_index += 1
                buffer = []
                word_count = 0

            # Si excede el límite, cerramos en punto semántico seguro
            if word_count + para_words > self.max_words and buffer:
                sections.append({
                    "section_id": f"SEC_{section_index}",
                    "text": "\n\n".join(buffer).strip()
                })
                section_index += 1
                buffer = []
                word_count = 0

            buffer.append(para)
            word_count += para_words

        # Última macrosección
        if buffer:
            sections.append({
                "section_id": f"SEC_{section_index}",
                "text": "\n\n".join(buffer).strip()
            })

        return self._post_validate_sections(sections)

    def _normalize_paragraphs(self, text: str) -> List[str]:
        # Divide por párrafos reales (no por saltos simples)
        raw = re.split(r'\n\s*\n', text)
        return [p.strip() for p in raw if p.strip()]

    def _post_validate_sections(self, sections: List[Dict]) -> List[Dict]:
        """
        Evita macrosecciones demasiado pequeñas fusionándolas
        con la siguiente (no se pierde información).
        """
        validated: List[Dict] = []
        carry = None

        for sec in sections:
            wc = len(sec["text"].split())
            if wc < 150:
                if carry:
                    carry["text"] += "\n\n" + sec["text"]
                else:
                    carry = sec
            else:
                if carry:
                    carry["text"] += "\n\n" + sec["text"]
                    validated.append(carry)
                    carry = None
                else:
                    validated.append(sec)

        if carry:
            validated.append(carry)

        # Reindexar IDs
        for i, sec in enumerate(validated, start=1):
            sec["section_id"] = f"SEC_{i}"

        return validated

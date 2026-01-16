import re
from typing import List, Dict
from pathlib import Path


def load_structural_patterns(pattern_file: Path) -> List[str]:
    """
    Carga patrones estructurales desde un archivo de texto.
    Si el archivo no existe, retorna una lista vacía (fallback seguro).
    """
    if not pattern_file.exists():
        return []

    patterns: List[str] = []
    with pattern_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)

    return patterns


class MacroSectionSplitter:
    """
    Divide el texto en macrosecciones por CAMBIO DE ESTRUCTURA ACADÉMICA,
    manteniendo coherencia semántica y sin perder información.
    """

    def __init__(self, max_words: int = 1800):
        self.max_words = max_words

        # Ruta al archivo de patrones estructurales
        pattern_path = Path(__file__).parent / "structural_patterns.txt"

        # Cargar patrones (si no existen, la lista queda vacía)
        self.structural_patterns = load_structural_patterns(pattern_path)

        # Compilar regex solo si hay patrones
        self.structural_regex = (
            re.compile("|".join(self.structural_patterns), re.IGNORECASE)
            if self.structural_patterns
            else None
        )

    def split(self, text: str) -> List[Dict]:
        paragraphs = self._normalize_paragraphs(text)

        sections: List[Dict] = []
        buffer: List[str] = []
        word_count = 0
        section_index = 1

        for para in paragraphs:
            para_words = len(para.split())

            # Detectar cambio de macrosección SOLO si hay patrones cargados
            is_new_macro_section = (
                bool(self.structural_regex.match(para.strip()))
                if self.structural_regex
                else False
            )

            # Si aparece un NUEVO encabezado estructural y ya hay contenido acumulado,
            # cerramos la macrosección actual
            if is_new_macro_section and buffer:
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
            if wc < 250:
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

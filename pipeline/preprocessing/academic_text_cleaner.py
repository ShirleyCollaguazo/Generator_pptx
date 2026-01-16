import re
from typing import Dict, List


# ===============================
# Patrones académicos (soft rules)
# ===============================

FRONT_START_PATTERNS = [
    r'^abstract\b',
    r'^resumen\b',
    r'^1\s+introducción\b',
    r'^1\.\s*introducción\b',
    r'^1\s+introduction\b',
    r'^1\.\s*introduction\b',
]

BACK_START_PATTERNS = [
    r'^references\b',
    r'^bibliografía\b',
    r'^referencias\b',
]


def remove_repeated_headers_footers(text: str, min_repeats: int = 3) -> str:
    """
    Elimina líneas cortas que se repiten muchas veces (headers/footers de PDF).
    Heurística suave: si no hay repetición clara, no elimina nada.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    if not lines:
        return text

    freq = {}
    for line in lines:
        if len(line) <= 80:
            freq[line] = freq.get(line, 0) + 1

    repeated = {
        line for line, count in freq.items()
        if count >= min_repeats
    }

    if not repeated:
        return text

    cleaned_lines = [
        line for line in lines
        if line not in repeated
    ]

    return "\n".join(cleaned_lines)

def remove_administrative_prefixes(text: str) -> str:
    """
    Elimina prefijos administrativos típicos incrustados en el texto académico.
    Solo actúa al inicio de línea (heurística segura).
    """
    admin_patterns = [
        r'^FORMATO\s+CONTROLADO[:\s].{0,60}',
        r'^FR\d{3,6}\/?\s*v?\d+(\.\d+)?\s*\/?\s*\d{2}-\d{2}-\d{4}',
    ]

    cleaned_lines = []

    for line in text.splitlines():
        original = line
        for pattern in admin_patterns:
            line = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
        cleaned_lines.append(line if line else original)

    return "\n".join(cleaned_lines)


def clean_academic_text(raw_text: str) -> Dict[str, str]:
    """
    Limpia texto académico separando:
    - title: título principal (si se detecta)
    - body: texto útil para análisis

    Heurísticas suaves:
    - Si no se detectan patrones, el texto no se modifica.
    - Nunca se elimina información por la fuerza.
    """

    raw_text = remove_repeated_headers_footers(raw_text)
    raw_text = remove_administrative_prefixes(raw_text)


    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    if not lines:
        return {
            "title": "",
            "body": raw_text
        }

    # 1. Extraer título (primera línea)
    title = lines[0]

    # 2. Detectar inicio del cuerpo
    body_start_idx = None
    for i, line in enumerate(lines):
        for pattern in FRONT_START_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                body_start_idx = i
                break
        if body_start_idx is not None:
            break

    # Si no se detecta inicio, no tocamos nada
    if body_start_idx is None:
        return {
            "title": title,
            "body": raw_text
        }

    body_lines = lines[body_start_idx:]

    # 3. Detectar inicio de referencias
    clean_body: List[str] = []
    for line in body_lines:
        if any(re.match(p, line, re.IGNORECASE) for p in BACK_START_PATTERNS):
            break
        clean_body.append(line)

    return {
        "title": title,
        "body": "\n\n".join(clean_body).strip()
    }

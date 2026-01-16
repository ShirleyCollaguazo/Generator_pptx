# pipeline/mapping/bullet_postprocess.py
import re
from typing import List

URL_START_RE = re.compile(r'^(https?:)?//', re.IGNORECASE)
HTTP_WORD_RE = re.compile(r'\bhttps?\b', re.IGNORECASE)

def postprocess_bullets(bullets: List[str]) -> List[str]:
    """
    Ajustes suaves para bullets generados desde texto académico:
    - Une bullets demasiado cortos (ej: "Resumen") con el siguiente
    - Evita cortes raros de URLs (http / //www / telegraph)
    - Elimina bullets basura (solo símbolos o 1-2 tokens sin sentido)
    Sin cambiar la lógica de generación del pipeline, solo limpieza final.
    """
    if not bullets:
        return bullets

    # 1) Normalizar espacios
    b = [" ".join(x.split()) for x in bullets if x and x.strip()]

    merged: List[str] = []
    i = 0

    while i < len(b):
        cur = b[i].strip()

        # --- Reglas de “basura” muy leve ---
        # Si es solo símbolos o muy corto y no aporta, intentar unirlo al siguiente
        cur_words = cur.split()
        is_symbols_only = bool(re.fullmatch(r"[-–—_/.:;]+", cur))
        is_too_short = len(cur_words) <= 2

        # --- Regla URL: si bullet actual parece "http" o termina en "http:" o es "http" suelto ---
        looks_like_http_fragment = (
            cur.lower() in {"http", "https", "http:", "https:"}
            or cur.lower().endswith("http")
            or cur.lower().endswith("http:")
            or HTTP_WORD_RE.search(cur) is not None and "://" not in cur
        )

        # --- Regla URL: si bullet actual es inicio tipo //www o similar ---
        looks_like_url_start = URL_START_RE.match(cur) is not None or cur.lower().startswith("www")

        # --- Regla: bullet tipo “Resumen” o etiqueta muy corta ---
        looks_like_label = cur.lower() in {"resumen", "abstract", "keywords", "palabras clave"}

        # Intentar merge con el siguiente
        if i + 1 < len(b):
            nxt = b[i + 1].strip()

            # A) Unir etiquetas cortas con el siguiente
            if looks_like_label and nxt:
                merged.append(f"{cur}: {nxt}")
                i += 2
                continue

            # B) Unir fragmentos URL con el siguiente
            if looks_like_http_fragment or looks_like_url_start:
                merged.append(f"{cur} {nxt}".strip())
                i += 2
                continue

            # C) Unir bullets demasiado cortos con el siguiente (pero sin forzar si el siguiente también es corto)
            if (is_symbols_only or is_too_short) and len(nxt.split()) >= 4:
                merged.append(f"{cur} {nxt}".strip())
                i += 2
                continue

        # Si no se unió, lo dejamos
        merged.append(cur)
        i += 1

    # 2) Filtrar basura final muy obvia (sin tocar contenido real)
    final: List[str] = []
    for x in merged:
        w = x.split()
        if len(w) == 0:
            continue
        # Si quedó un bullet de 1 palabra que no aporta, lo descartamos
        if len(w) == 1 and w[0].lower() in {"http", "https", "www"}:
            continue
        final.append(x)

    return final

from typing import Dict, List
from pipeline.mapping.bullet_postprocess import postprocess_bullets
from pipeline.mapping.bullet_decision import should_use_paragraph
import re




MAX_BULLETS_PER_SLICE = 3
MAX_WORDS_PER_BULLET = 25
MAX_TOTAL_WORDS_PER_SLICE = 90  # regla pedagógica
MAX_WORDS_PER_BULLET_HARD = 18
MAX_PARAGRAPH_WORDS = 80




def map_text_to_content(text: str) -> Dict:
    """
    Decide whether content should be rendered as paragraph or bullets.
    Marks content as overflow if it should be split into multiple slices.
    """

    text = text.strip()

    if should_use_paragraph(text):
        words = text.split()

        # Párrafo explicativo demasiado largo → bullets suaves
        if len(words) > 90:
            bullets = _split_into_bullets(
                text,
                max_bullets=3,
                max_words=22
            )
            bullets = postprocess_bullets(bullets)

            return {
                "content_type": "bullets",
                "bullets": bullets,
                "overflow": False
            }

        # Explicativo normal → párrafo
        return {
            "content_type": "paragraph",
            "text": text,
            "overflow": False
        }

    # si NO aplica should_use_paragraph → lógica original
    words = text.split()
    word_count = len(words)

    # ───────── CASE 1: Short paragraph ─────────
    if word_count <= 30:
        return {
            "content_type": "paragraph",
            "text": text,
            "overflow": False
        }

    # ───────── CASE 2: Medium text ─────────
    if 31 <= word_count <= 60:
        bullets = _split_into_bullets(
            text,
            max_bullets=2,
            max_words=MAX_WORDS_PER_BULLET
        )
        bullets = postprocess_bullets(bullets)

        return {
            "content_type": "bullets",
            "bullets": bullets,
            "overflow": False
        }

    # ───────── CASE 3: Long text ─────────
    bullets = _split_into_bullets(
        text,
        max_bullets=MAX_BULLETS_PER_SLICE,
        max_words=MAX_WORDS_PER_BULLET
    )

    bullets = postprocess_bullets(bullets)
    total_bullet_words = sum(len(b.split()) for b in bullets)
    max_bullet_len = max(len(b.split()) for b in bullets)

    overflow = (
        total_bullet_words > MAX_TOTAL_WORDS_PER_SLICE
        or max_bullet_len > MAX_WORDS_PER_BULLET_HARD
    )

    return {
        "content_type": "bullets",
        "bullets": bullets,
        "overflow": overflow
    }


def _split_into_bullets(
    text: str,
    max_bullets: int,
    max_words: int
) -> List[str]:
    """
    Split text into bullets, enforcing:
    - hard max_words per bullet
    - no orphan very-short bullets
    """

    sentences = (
        text.replace(";", ".")
        .replace(":", ".")
        .replace("•", ".")
        .split(".")
    )
    sentences = [s.strip() for s in sentences if s.strip()]

    bullets: List[str] = []

    for sentence in sentences:
        words = sentence.split()

        # Caso 1: oración corta
        if len(words) <= max_words:
            bullets.append(" ".join(words))

        # Caso 2: oración larga → dividir en chunks
        else:
            chunks = [
                words[i:i + max_words]
                for i in range(0, len(words), max_words)
            ]

            #  Fusionar último chunk si es muy corto
            if len(chunks) > 1 and len(chunks[-1]) < 5:
                chunks[-2].extend(chunks[-1])
                chunks.pop()

            for chunk in chunks:
                bullets.append(" ".join(chunk))

        if len(bullets) >= max_bullets:
            break

    return bullets[:max_bullets]


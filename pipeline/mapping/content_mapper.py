from typing import Dict, List


def map_text_to_content(text: str) -> Dict:
    """
    Decide whether content should be a paragraph or bullets
    based on word count and pedagogical rules.
    """

    words = text.split()
    word_count = len(words)

    # ───────── CASE 1: Short paragraph ─────────
    if word_count <= 30:
        return {
            "content_type": "paragraph",
            "text": text
        }

    # ───────── CASE 2: Medium text (2 bullets) ─────────
    if 31 <= word_count <= 60:
        bullets = _split_into_bullets(text, max_bullets=2, max_words=25)
        return {
            "content_type": "bullets",
            "bullets": bullets
        }

    # ───────── CASE 3: Long text (max 3 bullets) ─────────
    bullets = _split_into_bullets(text, max_bullets=3, max_words=25)
    return {
        "content_type": "bullets",
        "bullets": bullets
    }


def _split_into_bullets(
    text: str,
    max_bullets: int,
    max_words: int
) -> List[str]:
    """
    Split text into semantic-ish bullets using sentence boundaries
    and word limits.
    """

    sentences = text.replace(";", ".").split(".")
    sentences = [s.strip() for s in sentences if s.strip()]

    bullets: List[str] = []
    current = []

    for sentence in sentences:
        sentence_words = sentence.split()

        if len(current) + len(sentence_words) <= max_words:
            current.extend(sentence_words)
        else:
            bullets.append(" ".join(current))
            current = sentence_words

        if len(bullets) == max_bullets:
            break

    if current and len(bullets) < max_bullets:
        bullets.append(" ".join(current))

    return bullets

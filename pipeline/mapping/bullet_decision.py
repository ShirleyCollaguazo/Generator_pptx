import re

def should_use_paragraph(text: str) -> bool:
    """
    Heurística suave: devuelve True si el texto NO es apto para bullets
    (mejor mostrarlo como párrafo para no truncar sentido).
    """
    t = (text or "").strip()
    if not t:
        return True

    wc = len(t.split())

    # Muy corto: bullets no aportan
    if wc < 25:
        return True

    # Si termina "colgado" (indicador típico de corte previo o PDF roto)
    if re.search(r'\b(and|or|but|que|porque|de|del|la|el)\s*$', t, re.IGNORECASE):
        return True

    # Muchos conectores => texto explicativo continuo
    connectors = ["and", "or", "but", "however", "therefore", "que", "porque", "sin embargo", "por lo tanto"]
    connector_count = sum(t.lower().count(c) for c in connectors)
    if connector_count >= 3 and wc >= 35:
        return True

    # URLs / referencias largas suelen romper bullets
    if "http://" in t or "https://" in t:
        return True

    return False

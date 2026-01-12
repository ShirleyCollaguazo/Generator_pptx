from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

def detect_language(text: str, default_lang: str = "es") -> str:
    """
    Detects language of the given text.
    Falls back to default_lang for ambiguous cases.
    """
    try:
        lang = detect(text)
        # Defensive rule for Romance languages ambiguity
        if lang in {"pt", "ca"} and default_lang == "es":
            return "es"
        return lang
    except Exception:
        return default_lang


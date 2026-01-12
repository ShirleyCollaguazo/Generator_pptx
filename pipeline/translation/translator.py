import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_URL = "https://api.deepl.com/v2/translate"  # PRO endpoint

class DeepLTranslator:
    """
    Wrapper for DeepL translation API.
    """

    def __init__(self):
        if not DEEPL_API_KEY:
            raise ValueError("DEEPL_API_KEY not found in environment variables")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text or not text.strip():
            return text

        response = requests.post(
            DEEPL_URL,
            data={
                "auth_key": DEEPL_API_KEY,
                "text": text,
                "source_lang": source_lang.upper(),
                "target_lang": target_lang.upper(),
            },
            timeout=30
        )

        response.raise_for_status()
        return response.json()["translations"][0]["text"]

from dotenv import load_dotenv
import os
import requests

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_URL = "https://api.deepl.com/v2/translate"  # API PRO

def translate(text, source_lang, target_lang):
    response = requests.post(
        DEEPL_URL,
        data={
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
    )
    response.raise_for_status()
    return response.json()["translations"][0]["text"]

if __name__ == "__main__":
    texto_es = "Este es un texto académico de prueba para verificar la traducción automática."
    texto_en = translate(texto_es, "ES", "EN")
    texto_es_vuelta = translate(texto_en, "EN", "ES")

    print("ES → EN:", texto_en)
    print("EN → ES:", texto_es_vuelta)

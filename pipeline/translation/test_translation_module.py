from pipeline.translation.language_detector import detect_language
from pipeline.translation.translator import DeepLTranslator

translator = DeepLTranslator()

text_es = "Este sistema genera diapositivas académicas automáticamente."
lang = detect_language(text_es)

print("Idioma detectado:", lang)

if lang == "es":
    text_en = translator.translate(text_es, "ES", "EN")
    text_es_back = translator.translate(text_en, "EN", "ES")
    print("ES → EN:", text_en)
    print("EN → ES:", text_es_back)

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

BASE_MODEL = "t5-base"
ADAPTER_PATH = "models/title_model"   # carpeta donde entrenaste

# 1️⃣ Tokenizer
tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)

# 2️⃣ Modelo base
base_model = AutoModelForSeq2SeqLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

# 3️⃣ Cargar adapter LoRA
model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_PATH
)

model.eval()

# 4️⃣ Función de prueba
def generate_title(text):
    prompt = f"generate title: {text}"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    ).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=32,
        do_sample=False
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# =========================
# TEST
# =========================
sample_text = """
En la taxonomía o clasificación científica de los seres vivos, los animales (Animalia), también denominados antiguamente metazoos (Metazoa), constituyen un reino que agrupa a un extenso conjunto de organismos eucariotas, heterótrofos, pluricelulares y tisulares (con excepción de los poríferos).

Se caracterizan por su capacidad de movimiento, por carecer de cloroplasto (aunque existen excepciones, como en el caso de Elysia chlorotica)[4]​ y por la ausencia de pared celular. Además, presentan un desarrollo embrionario característico que incluye una fase de blástula, la cual determina un plan corporal fijo, aunque muchas especies pueden experimentar metamorfosis posterior, como ocurre en los artrópodos.

Los animales conforman un grupo natural estrechamente emparentado con los hongos (reino Fungi). Animalia es uno de los cinco reinos del dominio Eukaryota, y en él se incluye el ser humano.

"""
print("Predicted title:")
print(generate_title(sample_text))

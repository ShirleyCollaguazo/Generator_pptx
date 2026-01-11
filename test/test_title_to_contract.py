from pathlib import Path
from pipeline.inference.title_to_contract import write_titles_to_contract

contract_path = Path("pipeline/contracts/slide_contract_v1.json")

text = """
En la taxonomía o clasificación científica de los seres vivos, los animales (Animalia), también denominados antiguamente metazoos (Metazoa), constituyen un reino que agrupa a un extenso conjunto de organismos eucariotas, heterótrofos, pluricelulares y tisulares (con excepción de los poríferos).

Se caracterizan por su capacidad de movimiento, por carecer de cloroplasto (aunque existen excepciones, como en el caso de Elysia chlorotica)[4]​ y por la ausencia de pared celular. Además, presentan un desarrollo embrionario característico que incluye una fase de blástula, la cual determina un plan corporal fijo, aunque muchas especies pueden experimentar metamorfosis posterior, como ocurre en los artrópodos.

Los animales conforman un grupo natural estrechamente emparentado con los hongos (reino Fungi). Animalia es uno de los cinco reinos del dominio Eukaryota, y en él se incluye el ser humano.
"""

write_titles_to_contract(
    contract_path=contract_path,
    text=text,
    base_model_name="t5-base",
    adapter_path="models/title_model"
)

print("Outline generado y guardado correctamente.")

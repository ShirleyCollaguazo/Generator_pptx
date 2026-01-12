from dotenv import load_dotenv
import os

load_dotenv()  # 👈 ESTA línea es la clave

key = os.getenv("DEEPL_API_KEY")
print("DEEPL_API_KEY loaded:", bool(key))
print("First 6 chars:", (key[:6] + "..." if key else "None"))


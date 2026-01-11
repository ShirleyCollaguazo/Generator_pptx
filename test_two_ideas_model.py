import os
import torch
import PyPDF2
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class TwoIdeasModel:
    def __init__(
        self,
        model_dir="models/idea_model",
        max_input_len=2048,
        max_new_tokens=300
    ):
        self.model_dir = os.path.abspath(model_dir)
        self.max_input_len = max_input_len
        self.max_new_tokens = max_new_tokens
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if not os.path.exists(self.model_dir):
            raise FileNotFoundError(
                f"El directorio del modelo no existe: {self.model_dir}"
            )

        print(f"[*] Cargando modelo desde: {self.model_dir}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        
        if torch.cuda.is_available():
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_dir,
                dtype=torch.float16,
                device_map="auto"
            )
        else:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_dir)
            self.model = self.model.to(self.device)
        
        self.model.eval()
        self.model.config.use_cache = False

        print(f"[OK] Modelo cargado en: {self.device}")

    def chunk_text(self, text: str, max_tokens: int, overlap: int = 100) -> list:
        """Divide el texto en chunks basado en tokens"""
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        
        if len(tokens) <= max_tokens:
            return [text]
        
        chunks = []
        start = 0
        while start < len(tokens):
            end = start + max_tokens
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            chunks.append(chunk_text)
            start += max_tokens - overlap
        
        return chunks

    def generate(self, text: str) -> dict:
        """
        Genera dos ideas principales del texto.
        El texto debe estar en inglés.
        """
        # Preparar prompt base
        prompt_base = (
            "Extract exactly two distinct, high-level academic ideas from the following text.\n"
            "Each idea must be concise, non-overlapping, and faithful to the original content:\n"
        )
        
        # Calcular tokens del prompt base
        base_tokens = len(self.tokenizer.encode(prompt_base, add_special_tokens=False))
        max_text_tokens = self.max_input_len - base_tokens - 50  # Margen de seguridad
        
        # Contar tokens del texto
        text_tokens = len(self.tokenizer.encode(text, add_special_tokens=False))
        print(f"\n[*] Tokens del texto: {text_tokens}")
        print(f"[*] Tokens maximos permitidos: {max_text_tokens}")
        
        # Si el texto es muy largo, dividirlo en chunks
        if text_tokens > max_text_tokens:
            print(f"[!] El texto excede el limite. Dividiendo en chunks...")
            text_chunks = self.chunk_text(text, max_tokens=max_text_tokens, overlap=100)
            print(f"[*] Total de chunks: {len(text_chunks)}")
            
            all_ideas_1 = []
            all_ideas_2 = []
            
            for i, chunk in enumerate(text_chunks):
                chunk_tokens = len(self.tokenizer.encode(chunk, add_special_tokens=False))
                print(f"\n[*] Procesando chunk {i+1}/{len(text_chunks)} ({chunk_tokens} tokens)...")
                
                prompt = prompt_base + chunk
                prompt_tokens = len(self.tokenizer.encode(prompt, add_special_tokens=False))
                
                # INPUT
                print("\n" + "="*80)
                print(f"[INPUT] Chunk {i+1}/{len(text_chunks)}:")
                print("="*80)
                print(f"[*] Tokens del prompt: {prompt_tokens}")
                print(prompt)
                print("="*80)
                
                # Procesar chunk
                ideas = self._process_prompt(prompt)
                
                if ideas['idea_1']:
                    all_ideas_1.append(ideas['idea_1'])
                if ideas['idea_2']:
                    all_ideas_2.append(ideas['idea_2'])
            
            # Combinar ideas de todos los chunks
            combined_ideas = {
                'idea_1': ' '.join(all_ideas_1) if all_ideas_1 else '',
                'idea_2': ' '.join(all_ideas_2) if all_ideas_2 else ''
            }
            
            return combined_ideas
        else:
            # El texto cabe en un solo chunk
            prompt = prompt_base + text
            prompt_tokens = len(self.tokenizer.encode(prompt, add_special_tokens=False))
            
            # INPUT
            print("\n" + "="*80)
            print("[INPUT] AL MODELO:")
            print("="*80)
            print(f"[*] Tokens del prompt: {prompt_tokens}")
            print(prompt)
            print("="*80)
            
            return self._process_prompt(prompt)

    def _process_prompt(self, prompt: str) -> dict:
        """Procesa un prompt y retorna las ideas"""
        _, result = self._process_prompt_with_raw(prompt)
        return result
    
    def _process_prompt_with_raw(self, prompt: str) -> tuple:
        """Procesa un prompt y retorna (output_raw, ideas_parseadas)"""
        # Tokenizar
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_input_len
        )
        
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generar
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                num_beams=4,
                do_sample=False,
                early_stopping=False,
                no_repeat_ngram_size=3,
                length_penalty=1.2,
                min_length=50
            )

        # Decodificar
        raw_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # OUTPUT
        print("\n" + "="*80)
        print("[OUTPUT] DEL MODELO:")
        print("="*80)
        print(raw_output)
        print("="*80)

        # Parsear resultado
        ideas = self._parse_output(raw_output)
        
        return raw_output, ideas

    def _parse_output(self, output: str) -> dict:
        """Parsea el output del modelo"""
        output = output.strip()
        
        if "Main Idea 1:" in output and "Main Idea 2:" in output:
            parts = output.split("Main Idea 2:")
            idea_1 = parts[0].replace("Main Idea 1:", "").strip()
            idea_2 = parts[1].strip() if len(parts) > 1 else ""
            
            return {"idea_1": idea_1, "idea_2": idea_2}
        else:
            # Intentar dividir por líneas
            lines = output.split("\n")
            ideas = {"idea_1": "", "idea_2": ""}
            current_idea = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "idea 1" in line.lower() or "main idea 1" in line.lower():
                    current_idea = "idea_1"
                    ideas["idea_1"] = line.split(":", 1)[-1].strip() if ":" in line else ""
                elif "idea 2" in line.lower() or "main idea 2" in line.lower():
                    current_idea = "idea_2"
                    ideas["idea_2"] = line.split(":", 1)[-1].strip() if ":" in line else ""
                elif current_idea:
                    if ideas[current_idea]:
                        ideas[current_idea] += " " + line
                    else:
                        ideas[current_idea] = line
            
            return ideas

    def process_pdf(self, pdf_path: str, output_txt: str = None):
        """
        Procesa un PDF completo: lo divide en chunks y guarda input/output de cada chunk en un TXT
        
        Args:
            pdf_path: Ruta al archivo PDF
            output_txt: Ruta del archivo TXT de salida (por defecto: nombre_del_pdf_chunks.txt)
        """
        # Leer PDF
        print(f"\n[*] Leyendo PDF: {pdf_path}")
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo PDF no existe: {pdf_path}")
        
        # Extraer texto del PDF
        text = self._extract_text_from_pdf(pdf_path)
        print(f"[OK] Texto extraido: {len(text)} caracteres")
        
        # Preparar prompt base
        prompt_base = (
            "Extract exactly two distinct, high-level academic ideas from the following text.\n"
            "Each idea must be concise, non-overlapping, and faithful to the original content:\n"
        )
        
        # Calcular tokens del prompt base
        base_tokens = len(self.tokenizer.encode(prompt_base, add_special_tokens=False))
        max_text_tokens = self.max_input_len - base_tokens - 50  # Margen de seguridad
        
        # Dividir texto en chunks
        text_tokens = len(self.tokenizer.encode(text, add_special_tokens=False))
        print(f"[*] Tokens totales del texto: {text_tokens}")
        print(f"[*] Tokens maximos por chunk: {max_text_tokens}")
        
        text_chunks = self.chunk_text(text, max_tokens=max_text_tokens, overlap=100)
        print(f"[*] Total de chunks generados: {len(text_chunks)}")
        
        # Nombre del archivo de salida
        if output_txt is None:
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_txt = f"{pdf_name}_chunks.txt"
        
        # Procesar cada chunk y guardar resultados
        print(f"\n[*] Guardando resultados en: {output_txt}")
        
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(f"PROCESAMIENTO DE PDF: {os.path.basename(pdf_path)}\n")
            f.write(f"Total de chunks: {len(text_chunks)}\n")
            f.write("="*80 + "\n\n")
            
            for i, chunk in enumerate(text_chunks, 1):
                chunk_tokens = len(self.tokenizer.encode(chunk, add_special_tokens=False))
                print(f"\n[*] Procesando chunk {i}/{len(text_chunks)} ({chunk_tokens} tokens)...")
                
                prompt = prompt_base + chunk
                prompt_tokens = len(self.tokenizer.encode(prompt, add_special_tokens=False))
                
                # Escribir INPUT en el archivo
                f.write(f"\n{'='*80}\n")
                f.write(f"CHUNK {i}/{len(text_chunks)}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Tokens del chunk: {chunk_tokens}\n")
                f.write(f"Tokens del prompt: {prompt_tokens}\n\n")
                f.write("INPUT AL MODELO:\n")
                f.write("-"*80 + "\n")
                f.write(prompt + "\n")
                f.write("-"*80 + "\n\n")
                
                # Procesar chunk y obtener output raw
                raw_output, result = self._process_prompt_with_raw(prompt)
                
                # Escribir OUTPUT RAW en el archivo
                f.write("OUTPUT RAW DEL MODELO:\n")
                f.write("-"*80 + "\n")
                f.write(raw_output + "\n")
                f.write("-"*80 + "\n\n")
                
                # Escribir OUTPUT PARSEADO en el archivo
                f.write("OUTPUT PARSEADO:\n")
                f.write("-"*80 + "\n")
                f.write(f"Main Idea 1: {result['idea_1']}\n")
                f.write(f"Main Idea 2: {result['idea_2']}\n")
                f.write("-"*80 + "\n\n")
                
                print(f"[OK] Chunk {i} procesado y guardado")
        
        print(f"\n[OK] Procesamiento completo. Resultados guardados en: {output_txt}")

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"[*] Paginas en el PDF: {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    if page_num % 10 == 0:
                        print(f"  Procesadas {page_num} paginas...")
                
                print(f"[OK] Extraccion completa")
        except Exception as e:
            raise Exception(f"Error al extraer texto del PDF: {str(e)}")
        
        return text.strip()


if __name__ == "__main__":
    model_path = "models/idea_model"
    
    if not os.path.exists(model_path):
        print(f"[!] El directorio {model_path} no existe.")
        exit(1)
    
    print("[*] Cargando modelo...")
    model = TwoIdeasModel(model_dir=model_path)
    
    # Procesar PDF
    pdf_path = "./el principito.pdf"
    
    if os.path.exists(pdf_path):
        print("\n[*] Procesando PDF...")
        model.process_pdf(pdf_path)
    else:
        print(f"[!] El archivo PDF no existe: {pdf_path}")
        print("Usando texto de prueba...")
        
        # Texto de prueba (debe estar en inglés)
        sample_text = """
        Animals carry out the following essential functions: feeding, respiration, circulation, excretion, response, movement and reproduction.
        
        Feeding: Most animals cannot absorb food; they ingest it. Animals have evolved in various ways to feed themselves. Phagocytosis is the predominant or unique feeding mechanism in sponges, ctenophores, cnidarians and a subset of bilateral animals.
        
        Respiration: Whether they live in water or on land, all animals breathe; this means they can take in oxygen and release carbon dioxide. Thanks to their very simple bodies and thin walls, some animals use the diffusion of these substances through the skin. However, most animals have evolved complex tissues and organ systems for respiration.
        
        Circulation: Many small aquatic animals, such as some worms, use only diffusion to transport oxygen and nutrient molecules to all their cells, and collect waste products from them. Diffusion is sufficient because these animals are only a few cells thick. However, larger animals have some kind of circulatory system to move substances inside their bodies.
        """
        
        print("\n[*] EXTRAYENDO IDEAS PRINCIPALES...")
        result = model.generate(sample_text)
        
        print("\n[OK] RESULTADO PARSEADO:")
        print(f"Idea 1: {result['idea_1']}")
        print(f"Idea 2: {result['idea_2']}")


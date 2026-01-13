from typing import List, Dict
import re
import torch
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


MIN_IDEA_CHARS = 120  # regla formal: idea mínima


class IdeaGenerator:
    """
    Genera N ideas principales normalizadas a partir de una macrosección.
    """

    def __init__(
        self,
        model_dir: str | None = None,
        max_input_len: int = 2048,
        max_new_tokens: int = 400
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        #no se pasa model_dir, usar Hugging Face desde .env
        model_dir = model_dir or os.getenv("IDEA_MODEL_REPO")
        if not model_dir:
            raise ValueError("IDEA_MODEL_REPO is not set")

        hf_token = os.getenv("HF_TOKEN")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            token=hf_token
        )

        if torch.cuda.is_available():
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_dir,
                token=hf_token,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        else:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_dir,
                token=hf_token
            )
            self.model = self.model.to(self.device)

        self.model.eval()
        self.model.config.use_cache = False


    def generate_ideas(self, text: str) -> List[Dict[str, str]]:
        prompt = (
            "Extract the main academic ideas from the following text. "
            "Each idea must be a coherent explanatory paragraph. "
            "You may produce multiple ideas if the text covers multiple concepts.\n\n"
            f"{text}"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=400,
                num_beams=4,
                do_sample=False,
                no_repeat_ngram_size=3,
                length_penalty=1.1,
                min_length=100
            )

        raw_output = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        return self._normalize_ideas(raw_output)

    # ─────────────────────────────
    # 🔹 NORMALIZACIÓN (CLAVE)
    # ─────────────────────────────
    def _normalize_ideas(self, text: str) -> List[Dict[str, str]]:
        ideas = []

        # 🔹 Regex ULTRA tolerante a errores reales de LLM
        split_pattern = re.compile(
            r'(?i)(?:main\s+ide(?:a|ia|á|é)\s*\d*|ide(?:a|ia|á|é)\s*\d*)\s*:?',
        )

        # Dividir por etiquetas detectadas
        chunks = split_pattern.split(text)

        for chunk in chunks:
            clean = chunk.strip()
            if len(clean) >= MIN_IDEA_CHARS:
                ideas.append({"idea_text": clean})

        # 🔹 Fallback semántico: párrafos largos
        if len(ideas) <= 1:
            paragraphs = re.split(r'\n{2,}', text)
            ideas = []
            for p in paragraphs:
                p = p.strip()
                if len(p) >= MIN_IDEA_CHARS:
                    ideas.append({"idea_text": p})

        # 🔹 Último fallback absoluto
        if not ideas and len(text.strip()) >= MIN_IDEA_CHARS:
            ideas.append({"idea_text": text.strip()})

        for idea in ideas:
            idea["idea_text"] = re.sub(
                r'(?i)^\s*(main\s+ide(?:a|ia|á|é)\s*\d*\s*:?)',
                '',
                idea["idea_text"]
            ).strip()


        return ideas



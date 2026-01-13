import torch
import os
from typing import List
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel


class TitleGenerator:
    def __init__(
        self,
        base_model_name: str | None = None,
        adapter_path: str | None = None,
        device: str = None
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # usa el .env si no se pasan parámetros
        base_model_name = base_model_name or os.getenv("TITLE_BASE_MODEL")
        adapter_path = adapter_path or os.getenv("TITLE_ADAPTER_REPO")

        if not base_model_name:
            raise ValueError("TITLE_BASE_MODEL is not set")
        if not adapter_path:
            raise ValueError("TITLE_ADAPTER_REPO is not set")

        hf_token = os.getenv("HF_TOKEN")

        # Tokenizer DESDE el adapter
        self.tokenizer = AutoTokenizer.from_pretrained(
            adapter_path,
            token=hf_token
        )

        base_model = AutoModelForSeq2SeqLM.from_pretrained(
            base_model_name,
            token=hf_token,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )

        # Cargar LoRA 
        self.model = PeftModel.from_pretrained(
            base_model,
            adapter_path,
            token=hf_token
        )

        self.model.to(self.device)
        self.model.eval()

    def generate_titles(self, text: str) -> List[str]:
        # PROMPT CORRECTO (el mismo del entrenamiento)
        prompt = f"generate title: {text}"

        inputs = self.tokenizer(
            prompt,   
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=32,
                do_sample=False
            )

        titles = self.tokenizer.batch_decode(
            outputs,
            skip_special_tokens=True
        )

        return titles

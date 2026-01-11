import torch
from typing import List
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel


class TitleGenerator:
    def __init__(
        self,
        base_model_name: str,
        adapter_path: str,
        device: str = None
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Tokenizer DESDE el adapter
        self.tokenizer = AutoTokenizer.from_pretrained(adapter_path)

        base_model = AutoModelForSeq2SeqLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )

        # Cargar LoRA
        self.model = PeftModel.from_pretrained(base_model, adapter_path)
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

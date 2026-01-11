from typing import List, Dict
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class IdeaGenerator:
    def __init__(
        self,
        model_dir: str,
        max_input_len: int = 2048,
        max_new_tokens: int = 300
    ):
        self.model_dir = model_dir
        self.max_input_len = max_input_len
        self.max_new_tokens = max_new_tokens
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)

        if torch.cuda.is_available():
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_dir,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        else:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_dir)
            self.model = self.model.to(self.device)

        self.model.eval()
        self.model.config.use_cache = False

    def generate_ideas(self, text: str) -> Dict[str, str]:
        prompt = (
            "Extract exactly two distinct, high-level academic ideas from the following text.\n"
            "Each idea must be concise, non-overlapping, and faithful to the original content:\n\n"
            f"{text}"
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_input_len
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                num_beams=4,
                do_sample=False,
                no_repeat_ngram_size=3,
                length_penalty=1.2,
                min_length=50
            )

        raw_output = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        return self._parse_output(raw_output)

    def _parse_output(self, output: str) -> Dict[str, str]:
        output = output.strip()

        if "Main Idea 1:" in output:
            parts = output.split("Main Idea 2:")
            idea_1 = parts[0].replace("Main Idea 1:", "").strip()
            idea_2 = parts[1].strip() if len(parts) > 1 else ""
            return {
                "idea_1": idea_1,
                "idea_2": idea_2
            }

        return {"idea_1": output, "idea_2": ""}

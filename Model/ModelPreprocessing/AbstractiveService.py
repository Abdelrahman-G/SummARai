import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class AbstractiveService:
    def __init__(self):
        self.model_path = "fatmaserry/AraT5v2-arabic-summarization"
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

    """# ***Inference***"""

    def generate_summary(self, text,  max_length=1024):
        torch.cuda.empty_cache()  # Clear GPU cache before generation
        # Tokenize input
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt"
        ).to(self.model.device)

        # Generate summary
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_length=max_length,
                min_length=50,
                num_beams=2,  # faster inference
                length_penalty=1.0,
                no_repeat_ngram_size=3,
                early_stopping=True
            )

        # Decode output
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        return summary


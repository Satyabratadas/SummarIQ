import nltk
from nltk.tokenize import sent_tokenize
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Download punkt once
nltk.download("punkt")

class HierarchicalSummarizer:
    def __init__(self, model_name="google/flan-t5-base"):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    # ---------------------------
    # 1️⃣ Split into 3 sentence chunks
    # ---------------------------
    def split_into_chunks(self, text, max_sentences=3):
        sentences = sent_tokenize(text)
        chunks = []

        for i in range(0, len(sentences), max_sentences):
            chunk = " ".join(sentences[i:i + max_sentences])
            chunks.append(chunk)

        return chunks

    # ---------------------------
    # 2️⃣ Summarize a single chunk
    # ---------------------------
    def summarize_chunk(self, chunk):
        prompt = "summarize: " + chunk
        inputs = self.tokenizer.encode(
            prompt, return_tensors="pt", max_length=512, truncation=True
        )

        summary_ids = self.model.generate(
            inputs,
            max_length=80,
            min_length=20,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )

        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # ---------------------------
    # 3️⃣ Hierarchical summarize function
    # ---------------------------
    def summarize_section(self, section_text, final_pass=True):
        # Step 1: chunk the section
        chunks = self.split_into_chunks(section_text, max_sentences=3)

        # Step 2: summarize each chunk
        micro_summaries = [self.summarize_chunk(chunk) for chunk in chunks]

        # Step 3: merge all micro summaries
        combined_text = " ".join(micro_summaries)

        # Step 4: Optional final summary pass
        if final_pass:
            return self.summarize_chunk(combined_text)
        else:
            return combined_text

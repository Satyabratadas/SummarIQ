# summarizer.py

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer


class Summarizer:
    def __init__(self, model_path=None):
        # Load T5-small from local folder (saved model)
        self.model_name = model_path if model_path else "t5-small"

        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

    # T5 GENERATION 

    def t5_generate(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        out_ids = self.model.generate(
            inputs["input_ids"],
            num_beams=4,
            max_length=350,
            do_sample=False
        )
        return self.tokenizer.decode(out_ids[0], skip_special_tokens=True)

    # -------------------------------
    # Clean text functions
    # (copied exactly from notebook)
    # -------------------------------
    def clean_text_basic(self, text):
        text = text.replace("\n", " ").replace("\t", " ").strip()
        return " ".join(text.split())

    # -------------------------------
    # ABSTRACT SUMMARY (same prompt)
    # -------------------------------
    def summarize_abstract(self, abstract):
        clean_abst = self.clean_text_basic(abstract)

        prompt = f"""
            summarize this abstract into 3–4 crisp points focusing only on main idea, method, and contribution.
            Do not add anything new.

            Abstract:
            {clean_abst}
            """

        return self.t5_generate(prompt)

    # -------------------------------
    # SECTION SUMMARY (same prompt)
    # -------------------------------
    def summarize_section(self, section_name, section_text, equations=None):
        clean_sec = self.clean_text_basic(section_text)

        eq_block = ""
        if equations:
            eq_block = "\nImportant equations for context:\n" + "\n".join(equations[:5])

        prompt = f"""
Summarize the following section in 4–5 lines, keeping only the main idea and the technical insight.
Avoid repeating generic things. Do not include unrelated content.

Section: {section_name}

{eq_block}

Text:
{clean_sec}
"""

        return self.t5_generate(prompt)

    # -------------------------------
    # Equation Scoring (same as notebook)
    # -------------------------------
    def score_equation(self, eq):
        score = 0
        if any(sym in eq for sym in ["=", ":", "+", "-", "*", "^", "_"]):
            score += 2
        if "f" in eq or "F" in eq:
            score += 2
        if "I_f" in eq:
            score += 3
        if "K_X" in eq:
            score += 3
        if "P^" in eq or "P_" in eq:
            score += 2
        if any(v in eq for v in ["x", "y", "z"]):
            score += 2
        return score

    def get_top5_equations(self, equation_list):
        scored = [(eq, self.score_equation(eq)) for eq in equation_list]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in scored[:5]]

    # -------------------------------
    # FINAL JSON BUILDER (same as notebook)
    # -------------------------------
    def build_final_json(self, raw_paper, abstract_summary, section_chunks, section_summaries, top_equations):
        sections_out = []
        for chunk, summary in zip(section_chunks, section_summaries):
            sections_out.append({
                "section_name": chunk["section_name"],
                "section_summary": summary.strip()
            })

        important_equations = []
        for i, eq in enumerate(top_equations, start=1):
            important_equations.append({
                "equation_no": f"Equation {i}",
                "equation": eq
            })

        final_json = {
            "title": raw_paper["title"],
            "authors": raw_paper["authors"],
            "abstract_summary": abstract_summary,
            "sections": sections_out,
            "important_equations": important_equations
        }

        return final_json

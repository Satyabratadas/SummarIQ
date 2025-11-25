## Not mandatory delete this later

import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


# class Summarizer_base:
#     def __init__(self, model_path="t5-base", device=None):
#         print(f"Loading model from: {model_path}")

#         self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

#         self.tokenizer = AutoTokenizer.from_pretrained(model_path)
#         self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(self.device)

#         print(f"Model loaded on: {self.device}")


#     # -------------------------------------------------
#     # CLEAN SUMMARY
#     # -------------------------------------------------
#     def clean_summary(self, text):
#         if not text or text.strip() == "":
#             return "Summary generation failed."

#         text = re.sub(r"\$[^$]*\$", " ", text)
#         text = re.sub(r"\$\$[^$]*\$\$", " ", text)
#         text = re.sub(r"[#|&*{}_^\\\/]+", " ", text)
#         text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
#         text = re.sub(r"\|[^|]*\|", " ", text)
#         text = re.sub(r"(?i)section\s*\d+:?", " ", text)
#         text = re.sub(r"(?i)summary for section\s*\d+:?", " ", text)
#         text = re.sub(r"[-=]{2,}", " ", text)
#         text = re.sub(r"\s+", " ", text)

#         return text.strip()


#     # -------------------------------------------------
#     # ABSTRACT SUMMARY
#     # -------------------------------------------------
#     def summarize_abstract(self, abstract_text):
#         prompt = f"""
# You are summarizing ONLY the ABSTRACT of a scientific mathematics paper.

# Write a detailed academic summary (5–7 sentences) including:
# - the main problem,
# - the motivation,
# - the methods used (computational, ML, or geometric),
# - the key results,
# - the significance.

# Rules:
# - Summarize ONLY the abstract.
# - No LaTeX.
# - No equations.
# - No invented information.
# - Rewrite in new sentences.

# Abstract:
# {abstract_text}

# Write the abstract summary below:
# """

#         return self.t5_generate(prompt, max_length=240)


#     # -------------------------------------------------
#     # SECTION INSTRUCTIONS
#     # -------------------------------------------------
#     def get_section_instruction(self, section_name):
#         name = section_name.lower()

#         if "introduction" in name:
#             return "Describe the motivation, the main problem, and the general idea of their approach."

#         if "result" in name:
#             return "State the main mathematical findings, theorems, and surjectivity conditions."

#         if "experiment" in name or "example" in name:
#             return "Describe computational or ML methods, constructed examples, and empirical observations."

#         return "Summarize this section clearly and accurately."


#     # -------------------------------------------------
#     # BUILD SECTION PROMPT
#     # -------------------------------------------------
#     def build_summary_prompt(self, section_name, section_text, important_equations):
#         eq_text = "\n\n".join(important_equations)

#         instruction = self.get_section_instruction(section_name)

#         prompt = f"""
# You are summarizing a section of a mathematics research paper.

# Instruction: {instruction}

# Section Name: {section_name}

# Section Content:
# {section_text}

# Important Equations (for context, do not restate them):
# {eq_text}

# Write a clear section summary (5–7 sentences):
# """
#         return prompt


#     # -------------------------------------------------
#     # CHUNKING
#     # -------------------------------------------------
#     def split_into_chunks(self, text, max_tokens=200):
#         sentences = text.split(". ")
#         chunks, current = [], ""

#         for s in sentences:
#             if len(current.split()) + len(s.split()) < max_tokens:
#                 current += s + ". "
#             else:
#                 chunks.append(current.strip())
#                 current = s + ". "

#         if current:
#             chunks.append(current.strip())

#         return chunks


#     # -------------------------------------------------
#     # SECTION SUMMARY (multi-stage)
#     # -------------------------------------------------
#     def summarize_section(self, section_name, section_text, important_equations=None):
#         if important_equations is None:
#             important_equations = []

#         chunks = self.split_into_chunks(section_text, max_tokens=200)
#         partial_summaries = []

#         for c in chunks:
#             prompt = self.build_summary_prompt(section_name, c, important_equations)
#             partial_summaries.append(self.t5_generate(prompt, max_length=200))

#         combined = " ".join(partial_summaries)

#         final_prompt = f"""
# Combine the following partial summaries into a single clear summary (4–6 sentences):

# {combined}

# Final summary:
# """
#         return self.t5_generate(final_prompt, max_length=200)


#     # -------------------------------------------------
#     # EQUATION EXPLANATION
#     # -------------------------------------------------
#     def explain_equation(self, eq_latex):
#         prompt = f"""
# Explain the following LaTeX equation in simple mathematical terms:

# {eq_latex}

# Explain:
# 1. Meaning of variables.
# 2. Mathematical interpretation.
# 3. Any step-by-step reasoning (if possible).
# 4. Why it appears in the paper.
# 5. What structure or object it represents.

# Write a clear explanation:
# """
#         return self.t5_generate(prompt, max_length=220)


#     # -------------------------------------------------
#     # T5 GENERATOR
#     # -------------------------------------------------
#     def t5_generate(self, prompt, max_length=200):
#         inputs = self.tokenizer(
#             prompt,
#             return_tensors="pt",
#             truncation=True,
#             max_length=768
#         ).to(self.device)

#         outputs = self.model.generate(
#             inputs["input_ids"],
#             num_beams=2,
#             max_length=max_length,
#             do_sample=False,
#             no_repeat_ngram_size=3,
#             early_stopping=True
#         )

#         text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

#         if text.strip() == "":
#             return "Summary generation failed."

#         return self.clean_summary(text)


# import re
# import torch
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


# class Summarizer_base:
#     def __init__(self, model_path="t5-base"):
#         print(f"Loading T5-Base model (CPU) from: {model_path}")

#         self.device = "cpu"   # CPU ONLY (for Docker + local)

#         # Load tokenizer + model
#         self.tokenizer = AutoTokenizer.from_pretrained(model_path)
#         self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

#         self.model.to(self.device)
#         self.model.eval()

#         print("Model loaded on CPU ✓")

#     # ---------------------------------------------------------
#     # CLEAN SUMMARY OUTPUT
#     # ---------------------------------------------------------
#     def clean_summary(self, text):
#         if not text or text.strip() == "":
#             return "Summary generation failed."

#         text = re.sub(r"\$[^$]*\$", " ", text)
#         text = re.sub(r"\$\$[^$]*\$\$", " ", text)
#         text = re.sub(r"[#|&*{}_^\\\/]+", " ", text)
#         text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
#         text = re.sub(r"\s+", " ", text)
#         return text.strip()

#     # ---------------------------------------------------------
#     # FAST T5 GENERATION (CPU optimized)
#     # ---------------------------------------------------------
#     def t5_generate(self, prompt, max_length=180):

#         # smaller input window → MUCH faster on CPU
#         encoded = self.tokenizer(
#             prompt,
#             return_tensors="pt",
#             truncation=True,
#             max_length=150
#         )

#         with torch.no_grad():     # DISABLE gradients → faster
#             output_ids = self.model.generate(
#                 encoded["input_ids"],
#                 max_length=max_length,
#                 num_beams=1,          # greedy → fastest
#                 do_sample=False,
#                 early_stopping=True
#             )

#         text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

#         if text.strip() == "":
#             return "Summary generation failed."

#         return self.clean_summary(text)

#     # ---------------------------------------------------------
#     # ABSTRACT SUMMARY (T5-BASE friendly prompt)
#     # ---------------------------------------------------------
#     def summarize_abstract(self, abstract_text):
#         prompt = f"""
# Summarize the following abstract in 4–6 full academic sentences.
# Focus on: problem, motivation, method, main results, significance.
# Avoid LaTeX and equations.

# Abstract:
# {abstract_text}

# Summary:
# """
#         return self.t5_generate(prompt, max_length=180)

#     # ---------------------------------------------------------
#     # SECTION INSTRUCTION
#     # ---------------------------------------------------------
#     def get_instruction(self, sec):
#         sec = sec.lower()

#         if "introduction" in sec:
#             return "Explain the motivation, the problem, and the general approach."

#         if "result" in sec:
#             return "Describe the main mathematical findings and key results."

#         if "experiment" in sec or "example" in sec:
#             return "Describe computational or ML methods, constructed examples, and observations."

#         return "Summarize clearly and accurately."

#     # ---------------------------------------------------------
#     # SECTION SUMMARY
#     # ---------------------------------------------------------
#     def summarize_section(self, section_name, section_text, equations=None):
#         instruction = self.get_instruction(section_name)

#         eq_context = ""
#         if equations:
#             eq_context = "\n".join(equations)

#         prompt = f"""
# Summarize this section of a mathematics paper.

# Instruction: {instruction}

# Section Content:
# {section_text}

# Important Equations (for context, do not repeat them):
# {eq_context}

# Write a clear summary (4–6 sentences):
# """
#         return self.t5_generate(prompt, max_length=180)

#     # ---------------------------------------------------------
#     # EQUATION EXPLANATION
#     # ---------------------------------------------------------
#     def explain_equation(self, eq_str):
#         prompt = f"""
# Explain the meaning of the following equation:

# {eq_str}

# Explain:
# 1. Variables and symbols.
# 2. Mathematical interpretation.
# 3. Any steps or reasoning (if possible).
# 4. Why it appears in the paper.
# 5. What structure it represents.

# Explanation:
# """
#         return self.t5_generate(prompt, max_length=180)

import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class Summarizer_base:
    def __init__(self, model_path="t5-base"):
        print(f"Loading T5-Base model on CPU from: {model_path}")

        self.device = "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()

        print("Model loaded on CPU ✓")


    # ==========================================================
    # CLEAN SUMMARY TEXT
    # ==========================================================
    def clean_summary(self, text):
        if not text or text.strip() == "":
            return "Summary generation failed."

        text = re.sub(r"\$[^$]*\$", " ", text)
        text = re.sub(r"\$\$[^$]*\$\$", " ", text)
        text = re.sub(r"[#|&*{}_^\\\/]+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


    # ==========================================================
    # CLEAN & NORMALIZE MATHEMATICAL TEXT
    # ==========================================================
    def normalize_math_text(self, text):

        # Remove LaTeX commands
        text = re.sub(r"\\[a-zA-Z]+", " ", text)
        text = text.replace("{", " ").replace("}", " ")

        # Remove inline math
        text = re.sub(r"\$[^$]*\$", " ", text)
        text = re.sub(r"\$\$[^$]*\$\$", " ", text)

        # Convert common math symbols to words
        replacements = {
            "\\to": " maps to ",
            "\\mapsto": " maps to ",
            "→": " maps to ",
            "↦": " maps to ",
            "\\p^2": " projective plane ",
            "\\mathbb{P}^2": " projective plane ",
            "^": " ",
            "_": " ",
            "∈": " is in ",
            "∀": " for all ",
            "∃": " there exists ",
            "∴": " therefore ",
        }

        for sym, rep in replacements.items():
            text = text.replace(sym, rep)

        # Remove repeated spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()


    # ==========================================================
    # T5 GENERATOR (FAST CPU SETTINGS)
    # ==========================================================
    def t5_generate(self, prompt, max_length=180):
        encoded = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=150
        )

        with torch.no_grad():
            out_ids = self.model.generate(
                encoded["input_ids"],
                max_length=max_length,
                num_beams=1,            # FAST
                do_sample=False,
                early_stopping=True
            )

        text = self.tokenizer.decode(out_ids[0], skip_special_tokens=True)
        return self.clean_summary(text)


    # ==========================================================
    # REWRITE COMPLEX MATH INTO SIMPLE ENGLISH (Hybrid Step)
    # ==========================================================
    def rewrite_for_t5(self, text):

        prompt = f"""
Rewrite the following text into clear academic English.
Avoid LaTeX symbols. Expand mathematical expressions into words.

Text:
{text}

Rewritten:
"""

        rewritten = self.t5_generate(prompt, max_length=150)
        return rewritten


    # ==========================================================
    # ABSTRACT SUMMARY (Hybrid Pipeline)
    # ==========================================================
    def summarize_abstract(self, abstract_text):

        # 1. Clean & normalize math
        cleaned = self.normalize_math_text(abstract_text)

        # 2. Rewrite into simple English
        rewritten = self.rewrite_for_t5(cleaned)

        # 3. Summarize rewritten text
        prompt = f"""
Summarize the following abstract in 5–7 detailed academic sentences.
Explain the problem, motivation, methods, main results, and significance.

Abstract:
{rewritten}

Summary:
"""

        return self.t5_generate(prompt, max_length=180)


    # ==========================================================
    # SECTION INSTRUCTIONS
    # ==========================================================
    def get_instruction(self, name):
        name = name.lower()

        if "introduction" in name:
            return "Explain the motivation, the problem, and the approach."

        if "result" in name:
            return "Describe the key mathematical findings and results."

        if "experiment" in name or "example" in name:
            return "Explain the computational or ML methods and examples."

        return "Summarize clearly and accurately."


    # ==========================================================
    # SECTION SUMMARY (Hybrid Pipeline)
    # ==========================================================
    def summarize_section(self, section_name, section_text, equations=None):

        # 1. Clean math
        cleaned = self.normalize_math_text(section_text)

        # 2. Rewrite for T5-Base
        rewritten = self.rewrite_for_t5(cleaned)

        instruction = self.get_instruction(section_name)

        prompt = f"""
{instruction}

Section:
{rewritten}

Write a clear summary in 4–6 sentences:
"""

        return self.t5_generate(prompt, max_length=180)


    # ==========================================================
    # EQUATION EXPLANATION
    # ==========================================================
    def explain_equation(self, eq):
        cleaned = self.normalize_math_text(eq)

        prompt = f"""
Explain the meaning of the following equation in simple English.
Avoid symbolic notation. Focus on interpretation.

Equation:
{cleaned}

Explain in 3–5 sentences:
- variables used
- meaning
- interpretation
- why it appears in the paper

Explanation:
"""

        return self.t5_generate(prompt, max_length=180)

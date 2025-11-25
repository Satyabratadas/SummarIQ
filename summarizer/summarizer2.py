import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class Summarizer2:
    def __init__(self, model_path):
        print(f"Loading T5 summarizer model from: {model_path}")

        # Device selection
        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self.model.to(self.device)

        print(f"Model loaded on: {self.device}")

    # ---------------------------------------------------------
    # generate
    # ---------------------------------------------------------
    def t5_generate(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        out_ids = self.model.generate(
            inputs["input_ids"],
            num_beams=2,
            max_length=350,
            early_stopping=True,
            no_repeat_ngram_size=3
        )

        return self.tokenizer.decode(out_ids[0], skip_special_tokens=True)

    # ---------------------------------------------------------
    # clean summary
    # ---------------------------------------------------------
    def clean_summary(self, text):
        if not text:
            return ""

        text = re.sub(r"\$[^$]*\$", "", text)
        text = re.sub(r"\$\$[^$]*\$\$", "", text)
        text = re.sub(r"[#|&*{}_^\\\/]+", " ", text)
        text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
        text = re.sub(r"\|[^|]*\|", " ", text)
        text = re.sub(r"(?i)section\s*\d+:?", "", text)
        text = re.sub(r"(?i)summary for section\s*\d+:?", "", text)
        text = re.sub(r"[-=]{2,}", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ---------------------------------------------------------
    # chunk builder
    # ---------------------------------------------------------
    def build_section_chunks(self, paper):
        chunks = []
        for sec in paper["sections"]:
            chunks.append({
                "title": paper["title"],
                "abstract": paper["abstract"],
                "section_name": sec["name"],
                "section_content": sec["content"]
            })
        return chunks

    # ---------------------------------------------------------
    # equation format
    # ---------------------------------------------------------
    def format_equation_for_summary(self, eq):
        eq = eq.replace("\\\\", "\\\\\n")
        return f"```latex\n{eq}\n```"

    # ---------------------------------------------------------
    # pick top equations
    # ---------------------------------------------------------
    def pick_top_equations_raw(self, paper, top_k=5):
        eqs = paper.get("equations", [])
        return eqs[:top_k]

    # ---------------------------------------------------------
    # split chunks
    # ---------------------------------------------------------
    def split_into_chunks(self, text, max_tokens=300):
        sentences = text.split(". ")
        chunks, current = [], ""

        for s in sentences:
            if len(current.split()) + len(s.split()) < max_tokens:
                current += s + ". "
            else:
                chunks.append(current.strip())
                current = s + ". "
        if current:
            chunks.append(current.strip())
        return chunks

    # ---------------------------------------------------------
    # abstract summary
    # ---------------------------------------------------------
    def summarize_abstract(self, paper):
        prompt = f"""
        you are summarizing ONLY the abstract of a scientific research paper.

        Write a detailed academic summary that is 5–7 sentences long.
        Your summary MUST include:
        - the main problem or object studied,
        - the motivation or context (if implied),
        - the methods or approach used (e.g., computation, ML, geometry),
        - the key results or theorems,
        - the significance of those results.

        Strict rules:
        - Summarize ONLY the abstract, NOT any section.
        - Use clear academic writing, not bullet points.
        - DO NOT include equations or LaTeX.
        - DO NOT add new claims beyond what is described.
        - DO NOT shorten the meaning; expand it into full sentences.
        - DO NOT copy the abstract wording; rewrite in new sentences.

        Abstract Text:
        {paper['abstract']}

        ---
        Write the abstract summary below (5–7 full sentences):
        """
        output = self.t5_generate(prompt)
        return self.clean_summary(output)

    # ---------------------------------------------------------
    # section instruction
    # ---------------------------------------------------------
    def get_section_instruction(self, section_name):
        name = section_name.lower()

        if "introduction" in name:
            return """
            Summarize the INTRODUCTION by focusing on:
            - the motivation for the research,
            - what problem the authors want to solve,
            - why the problem is important,
            - the general idea of their approach.
            Do NOT include detailed results or experiments.
            """

        if "result" in name:
            return """
            Summarize the RESULTS section by focusing on:
            - the main theorems or mathematical claims,
            - the surjectivity criterion,
            - how the indeterminacy locus I_f determines surjectivity.
            Do NOT talk about motivation or experiments.
            """

        if "experiment" in name or "example" in name:
            return """
            Summarize the EXPERIMENTS/EXAMPLES section by focusing on:
            - the computational or ML methods used,
            - how Python or algorithms generated examples,
            - new explicit maps the authors constructed,
            - empirical observations that support the theory.
            Do NOT describe theorems.
            """

        return "Summarize this section accurately and clearly."

    # ---------------------------------------------------------
    # build summary prompt
    # ---------------------------------------------------------
    def build_summary_prompt(self, chunk, top_equations):
        eq_text = "\n\n".join(self.format_equation_for_summary(eq) for eq in top_equations)
        section_instruction = self.get_section_instruction(chunk["section_name"])

        prompt = f"""
        You are summarizing a section of a scientific mathematics paper.
        Follow the instructions below to summarize correctly.

        {section_instruction}

        Section Name: {chunk['section_name']}
        Section Content:
        {chunk['section_content']}

        Important Equations:
        {eq_text}

        Write a detailed, clear, human-friendly summary (5–7 sentences).
        """
        return prompt

    # ---------------------------------------------------------
    # summarize section
    # ---------------------------------------------------------
    def summarize_section(self, section, top_equations):
        content = section["section_content"]

        # STEP 1
        small_chunks = self.split_into_chunks(content, max_tokens=250)

        partial_summaries = []

        # STEP 2
        for chunk_text in small_chunks:
            prompt = self.build_summary_prompt(
                {"section_name": section["section_name"], "section_content": chunk_text},
                top_equations
            )
            summary = self.t5_generate(prompt)
            partial_summaries.append(self.clean_summary(summary))

        # STEP 3
        combined = " ".join(partial_summaries)

        # STEP 4
        final_prompt = f"""
        Section: {section['section_name']}

        Combine and compress the following partial summaries into ONE clear section summary:

        {combined}

        Output ONLY the final summary (3–5 sentences).
        """
        final_summary = self.t5_generate(final_prompt)
        return self.clean_summary(final_summary)

    # ---------------------------------------------------------
    # explain equation
    # ---------------------------------------------------------
    def explain_equation(self, eq_latex):
        prompt = (
            "The following is a LaTeX mathematical equation:\n\n"
            "```latex\n"
            f"{eq_latex}\n"
            "```\n\n"
            "Explain the equation clearly:\n"
            "1. Meaning of variables.\n"
            "2. Mathematical interpretation.\n"
            "3. Step-by-step derivation (as far as possible).\n"
            "4. Why this equation appears in the paper.\n"
            "5. What mathematical object/structure it represents.\n"
        )
        out = self.t5_generate(prompt)
        return self.clean_summary(out)



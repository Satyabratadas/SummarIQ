from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import re


class Summarizer:
    def __init__(self, model_path):
        print(f'Loading T5 summarizer model from: {model_path}')

        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        
        ## Load tokenizer and model 
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

        self.model.to(self.device)

        print(f"Model successfully loaded on device: {self.device}")

    def t5_generate(self, prompt, max_length=350):
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)

        out_ids = self.model.generate(
            inputs["input_ids"],
            num_beams=4,
            max_length=max_length,
            do_sample=False,
            no_repeat_ngram_size=3
        )

        summary = self.tokenizer.decode(out_ids[0], skip_special_tokens=True)
        return self.clean_summary(summary)

    def clean_summary(self, text):
        if not text:
            return ""

        text = re.sub(r"\$[^$]*\$", "", text)
        text = re.sub(r"\$\$[^$]*\$\$", "", text)
        text = re.sub(r"[#|&*{}_^\\\/]+", " ", text)
        text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
        text = re.sub(r"\|[^|]*\|", " ", text)
        text = re.sub(r"(?i)section\s*\d+:?", "", text)
        text = re.sub(r"(?i)summary for section\s*\d+:?", "", text)
        text = re.sub(r"[-=]{2,}", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    
    def summarize_abstract(self, abstract_text):
        prompt = f"""
            ou are summarizing ONLY the abstract of a scientific research paper.

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
            {abstract_text}

            ---
            Write the abstract summary below (5–7 full sentences):
                """
        return self.t5_generate(prompt, max_length=300)
    
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
    
    def build_summary_prompt(self, section_name, section_text, important_equations):
        eq_text = "\n\n".join(f"```latex\n{eq}\n```" for eq in important_equations)
        section_instruction = self.get_section_instruction(section_name)
        prompt = f"""
            You are summarizing a section of a scientific mathematics paper.
            Follow the instructions below to summarize correctly.

            {section_instruction}

            Section Name: {section_name}

            Section Content:
            {section_text}

            Important Equations:
            {eq_text}

            Write a detailed, clear, human-friendly summary (5–7 sentences).
            """

        return prompt
    
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
    
    def summarize_section(self, section_name, section_text, important_equations=None):
        if important_equations is None:
            important_equations = []

        # Step 1: split into small chunks
        small_chunks = self.split_into_chunks(section_text, max_tokens=250)
        partial_summaries = []

        # Step 2: summarize each chunk separately
        for chunk_text in small_chunks:
            prompt = self.build_summary_prompt(section_name, chunk_text, important_equations)
            partial_summaries.append(self.t5_generate(prompt))

        # Step 3: combine summaries
        combined_summary = " ".join(partial_summaries)

        # Step 4: compress final summary
        final_prompt = f"""
                Combine and compress the following partial summaries into a single clear summary (3–5 sentences):

                {combined_summary}

                Output ONLY the final summary below:
                """
        return self.t5_generate(final_prompt, max_length=300)
    
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
        return self.t5_generate(prompt, max_length=350)
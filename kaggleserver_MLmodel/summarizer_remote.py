# import torch
# import re
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import requests



class SummarizerRemote:

    def __init__(self, model_path="google-t5/t5-small"):

        self.NGROK_URL = "https://lakisha-deltaic-conception.ngrok-free.dev"

    ##  EQUATION SCORING
    
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
            score += 1

        score += min(len(eq) // 40, 2)
        return score

    def get_top5_from_extracted(self, equations):
        scored = [(eq, self.score_equation(eq)) for eq in equations]
        scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
        return [eq for eq, score in scored_sorted[:5]]

    ##      CLEAN TEXT 

    def clean_text(self, text):
        text = re.sub(r"\$[^$]*\$", " ", text)
        text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.DOTALL)
        text = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})?", " ", text)
        text = re.sub(r"\{[^{}]*\}", " ", text)
        text = re.sub(r"\[[^\]]*\]", " ", text)
        text = re.sub(r"\([^)]*\)", " ", text)
        text = re.sub(r"\[\d+\]", " ", text)
        text = re.sub(r"\b(Figure|cf|Cf|Remark|Proposition|Lemma)\b[^.]*\.", " ", text)
        text = re.sub(r"\b[a-zA-Z]\b", " ", text)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        text = re.sub(r"[\(\)\[\]\{\}]", " ", text)
        text = re.sub(r"[,;:]+", " ", text)
        text = re.sub(r"[\|\^\_\=\*\+\-\/]+", " ", text)
        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r"for .*?:", " ", text)
        text = re.sub(r"return .*", " ", text)
        text = re.sub(r"[A-Za-z0-9_]+\.[A-Za-z0-9_]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def clean_paper_for_t5(self, paper):
        cleaned = {}
        cleaned["abstract"] = self.clean_text(paper.get("abstract", ""))

        cleaned_secs = []
        for sec in paper.get("sections", []):
            cleaned_secs.append({
                "name": self.clean_text(sec.get("name", "")),
                "content": self.clean_text(sec.get("content", ""))
            })
        cleaned["sections"] = cleaned_secs
        return cleaned

    ## T5 GENERATE 

    def t5_generate(self, prompt, max_len=150):
         ## use kaggle T5 api
        url = self.NGROK_URL + "/generate"
        res = requests.post(url, json={"prompt": prompt})
        try:
            return res.json().get("text", "")
        except:
            print("Remote server error:", res.text)
            return ""

   

    ## Remove summary promt after summarise the chunk
    def strip_prompt_artifacts(self, text):
        patterns = [
            r"(?i)Write a clear academic summary of the following abstract.*",
            r"(?i)write\s*5[\–\-]?\s*7.*?sentences[:\.]?",
            r"(?i)write\s*\d.*?sentences[:\.]?",
            r"(?i)abstract[:\.]?",
            r"(?i)summarise this chunk.*",
            r"(?i)summarize this chunk.*",
            r"(?i)summarize the following.*",
            r"(?i)Summarize the following text in 2 sentences:*",
            r"(?i)in 2 sentences:*",
            r"(?i)Begin the first sentence with a phrase like*",
            r"(?i)summarize in.*",
            r"(?i)Summary:.*",
            r"(?i)Abstract:*",
            r"(?i)first summary.*",
            r"(?i)second summary.*",
            r"(?i)good academic structure.*",
            r"(?i)abstract:.*",
            r"(?i)this chunk.*",
            r"(?i)this chapter.*",
            r"(?i)write.*academic.*",
            r"(?i)avoid.*",
            r"\.{2,}",
            r"[\"\']{1,}",
        ]
        
        cleaned = text
        for p in patterns:
            cleaned = re.sub(p, "", cleaned)
            
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

     ##  ABSTRACT SUMMARY 

    def summarize_abstract(self, paper):
        abstract = paper["abstract"]

        prompt = (
            "Write a clear academic summary of the following abstract. "
            "Begin the first sentence with a phrase like 'This paper investigates', "
            "'This work studies', or 'The authors analyze'. "
            "Explain the main problem, the methods used, the central results, "
            "and why they matter. Do not copy any exact sentences. "
            "Write 5–7 complete scientific sentences.\n\n"
            "Abstract:\n"
            + abstract
            + "\n\nAcademic summary:"
        )
        abs_summary = self.t5_generate(prompt)
        return self.strip_prompt_artifacts(abs_summary)

    ## SECTION SUMMARIES 

    def build_chunk_prompt(self, chunk):
        return "Summarize the following text in 2 sentences:" + chunk + "Summary:"

    def split_into_chunks(self, text, max_words=180):
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunks.append(" ".join(words[i:i+max_words]))
            i += max_words
        return chunks

    def summarize_chunk(self, chunk):
        prompt = self.build_chunk_prompt(chunk)
        return self.t5_generate(prompt)

    def summarize_section_t5(self, section_text):
        chunks = self.split_into_chunks(section_text, 180)

        partial_summaries = []
        for chunk in chunks:
            summary = self.summarize_chunk(chunk)
            clean_summary = self.strip_prompt_artifacts(summary)
            partial_summaries.append(clean_summary)

        return " ".join(partial_summaries)

    def summarize_section(self, sec):
        section_name = sec["name"]
        section_text = sec["content"]
        summary = self.summarize_section_t5(section_text)
        return {
            "section_name": section_name,
            "summary": summary
        }

    ##  FINAL JSON BUILDER 
    def build_final_json(self, abstract_summary, section_summaries, important_top5, raw_paper):
        sections_out = []
        for sec in section_summaries:
            sections_out.append({
                "section_name": sec["section_name"],
                "section_summary": sec["summary"].strip()
            })

        important_equations = []
        for i, eq in enumerate(important_top5, 1):
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

   
    ## MAIN ENTRY POINT 
    def summarize(self, paper):
        cleaned_paper = self.clean_paper_for_t5(paper)

        equations = paper.get("equations", [])
        important_top5 = self.get_top5_from_extracted(equations)

        abstract_summary = self.summarize_abstract(cleaned_paper)

        section_summaries = []
        for sec in cleaned_paper["sections"]:
            section_summaries.append(self.summarize_section(sec))

        final_json = self.build_final_json(
            abstract_summary=abstract_summary,
            section_summaries=section_summaries,
            important_top5=important_top5,
            raw_paper=paper
        )

        return final_json
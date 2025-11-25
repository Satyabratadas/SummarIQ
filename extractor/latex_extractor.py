import os
import re
import json
import uuid

class LatexExtractor:
    def __init__(self, folder_path= "data/Test_pdf/sm.tex", output_path="data/latex_extracted.json"):
        self.folder_path = folder_path
        self.output_path = output_path
        self.all_files_data = []

    # CLEAN LATEX COMMANDS
    def clean_latex(self, text):
        text = re.sub(r"\\cite\{.*?\}", "", text)
        text = re.sub(r"\\ref\{.*?\}", "", text)
        text = re.sub(r"\\[a-zA-Z]+\*", "", text)
        text = re.sub(r"\\[a-zA-Z]+\{.*?\}", "", text)
        text = re.sub(r"\\[a-zA-Z]+", "", text)
        text = text.replace("{", "").replace("}", "")
        return text

    def extract_sections_from_file(self, file_path, file_name):

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # --- TITLE ---
        title_match = re.search(r"\\title\{(.+?)\}", content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else None

        # --- AUTHORS ---
        authors = re.findall(r"\\author\{(.+?)\}", content, re.DOTALL)

        # --- ABSTRACT ---
        abstract_match = re.search(r"\\begin\{abstract\}(.+?)\\end\{abstract\}", content, re.DOTALL)
        abstract = self.clean_latex(abstract_match.group(1).strip()) if abstract_match else ""

        # --- ALL EQUATIONS (global) ---
        all_equations = []
        eq_patterns = [
            r"\\begin\{equation\}(.+?)\\end\{equation\}",
            r"\\begin\{align\}(.+?)\\end\{align\}",
            r"\\\[(.+?)\\\]",
            r"\$\$(.+?)\$\$",
            r"\$(.+?)\$"
        ]

        for pattern in eq_patterns:
            all_equations += [eq.strip() for eq in re.findall(pattern, content, re.DOTALL)]

        # --- SECTIONS ---
        section_pattern = r"\\section\*?\{(.+?)\}"
        sec_positions = list(re.finditer(section_pattern, content))

        sections = []

        for i, match in enumerate(sec_positions):
            sec_name = match.group(1).strip()
            start = match.end()
            end = sec_positions[i+1].start() if i+1 < len(sec_positions) else len(content)

            sec_text = content[start:end].strip()
            sec_clean = self.clean_latex(sec_text)

            sections.append({
                "name": sec_name,
                "content": sec_clean
            })

        # --- FULL CLEAN TEXT ---
        full_clean_text = self.clean_latex(content)

        return {
            "file_name": file_name,
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "sections": sections,
            "equations": all_equations[:10],   # return top 10 eqns
            "full_text": full_clean_text
        }

    def process_all_files(self):
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".tex"):
                file_path = os.path.join(self.folder_path, file_name)
                data = self.extract_sections_from_file(file_path, file_name)
                self.all_files_data.append(data)

    def save_to_json(self):
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.all_files_data, f, indent=2, ensure_ascii=False)

        print("Saved to", self.output_path)

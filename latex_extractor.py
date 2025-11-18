import os
import re
import json
import uuid

# class LatexExtractor:
#     def __init__(self, folder_path, output_path= "latex_extracted.json"):
#         self.folder_path = folder_path
#         self.all_files_data = []
#         self.output_path = output_path
    
#     def extract_sections_from_file(self, file_path, file_name):

#         ## """Extract sections, equations, theorems, etc. from a single LaTeX file"""
#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read()

#         # Extract title
#         title_match = re.search(r'\\title(?:\[[^\]]*\])?\s*\{([\s\S]*?)\}', content, re.DOTALL)

#         title = title_match.group(1).strip() if title_match else None

#         # Extract authors (supporting multiple)
#         author_pattern = r'\\author(?:\[[^\]]*\])?\{(.+?)\}'
#         authors = [a.strip() for a in re.findall(author_pattern, content, re.DOTALL)]

#         ## Find all \section{...} labels
#         section_pattern = r'\\section\{(.+?)\}(?:\s*\\label\{(.+?)\})?'
#         matches = list(re.finditer(section_pattern, content, re.DOTALL))

#         sections = []

#         for i, match in enumerate(matches):
#             sec_name = match.group(1).strip()
#             sec_label = match.group(2) if match.group(2) else None
#             start = match.end()
#             end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
#             sec_content = content[start:end].strip()

#             ## Extract key environments
#             equations = [eq.strip() for eq in re.findall(r'\\begin\{equation\}(.+?)\\end\{equation\}', sec_content, re.DOTALL)]
#             equations += [eq.strip() for eq in re.findall(r'\$\$(.+?)\$\$', sec_content, re.DOTALL)]
#             equations += [eq.strip() for eq in re.findall(r'\\\[(.+?)\\\]', sec_content, re.DOTALL)]

#             theorems = [t.strip() for t in re.findall(r'\\begin\{theorem\}(.+?)\\end\{theorem\}', sec_content, re.DOTALL)]
#             lemmas = [l.strip() for l in re.findall(r'\\begin\{lemma\}(.+?)\\end\{lemma\}', sec_content, re.DOTALL)]
#             definitions = [d.strip() for d in re.findall(r'\\begin\{definition\}(.+?)\\end\{definition\}', sec_content, re.DOTALL)]

#             sections.append({
#                 "name": sec_name,
#                 "label": sec_label,
#                 "content": sec_content,
#                 "equations": equations,
#                 "theorems": theorems,
#                 "lemmas": lemmas,
#                 "definitions": definitions
#             })

#         ## Attach file metadata
#         file_id = str(uuid.uuid4())

#         return{
#             "file_id": file_id,
#             "file_name": file_name,
#             "authors": authors,
#             "title": title,
#             "sections": sections
#         }



#     ## process all .tex files in the given folder
#     def process_all_files(self):
#         for file_name in os.listdir(self.folder_path):
#             if file_name.endswith(".tex"):
#                 file_path = os.path.join(self.folder_path, file_name)
#                 file_data = self.extract_sections_from_file(file_path, file_name)
#                 self.all_files_data.append(file_data)

#     ## save the extracted latex data to a json file   
#     def save_to_json(self):
#         with open(self.output_path, "w", encoding="utf-8") as f:
#             json.dump(self.all_files_data, f, indent=2, ensure_ascii=False)

#         print(" Extraction complete! Data saved to latex_extracted.json")

#     ## get summary with section wise from the latex file 
#     def get_summary(self):
#         return [
#             {"file_name": f["file_name"], "num_sections": len(f["sections"])}
#             for f in self.all_files_data
#         ]

class LatexExtractor:
    def __init__(self, folder_path, output_path="latex_extracted.json"):
        self.folder_path = folder_path
        self.all_files_data = []
        self.output_path = output_path

    def extract_sections_from_file(self, file_path, file_name):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title
        title_match = re.search(r'\\title(?:\[[^\]]*\])?\s*\{([\s\S]*?)\}', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else None

        # Extract authors
        author_pattern = r'\\author(?:\[[^\]]*\])?\{(.+?)\}'
        authors = [a.strip() for a in re.findall(author_pattern, content, re.DOTALL)]

        # Remove LaTeX commands for cleaner text
        clean_text = re.sub(r'\\(begin|end)\{.*?\}', '', content)
        clean_text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^\}]*\})?', '', clean_text)
        clean_text = re.sub(r'%.*', '', clean_text)  # remove comments
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        # Extract equations globally (not sectionwise)
        equations = []
        equations += [eq.strip() for eq in re.findall(r'\\begin\{equation\}(.+?)\\end\{equation\}', content, re.DOTALL)]
        equations += [eq.strip() for eq in re.findall(r'\$\$(.+?)\$\$', content, re.DOTALL)]
        equations += [eq.strip() for eq in re.findall(r'\\\[(.+?)\\\]', content, re.DOTALL)]

        # Attach file metadata
        file_id = str(uuid.uuid4())

        full_text = self.clean_latex_text(clean_text)
        return {
            "file_id": file_id,
            "file_name": file_name,
            "authors": authors,
            "title": title,
            "text": full_text,
            "equations": equations
        }

    def process_all_files(self):
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".tex"):
                file_path = os.path.join(self.folder_path, file_name)
                file_data = self.extract_sections_from_file(file_path, file_name)
                self.all_files_data.append(file_data)

    def save_to_json(self):
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.all_files_data, f, indent=2, ensure_ascii=False)
        print(" Extraction complete! Data saved to", self.output_path)

    def get_summary(self):
        return [
            {
                "file_name": f["file_name"],
                "num_equations": len(f["equations"]),
                "text_length": len(f["text"])
            }
            for f in self.all_files_data
        ]
    
    def clean_latex_text(self,raw_text):
    # 1. Remove LaTeX commands like \command{...}, \command[...]{...}, etc.
        text = re.sub(r'\\[a-zA-Z@]+(\*?)\s*(\[[^\]]*\])?(\{[^\}]*\})?', '', raw_text)
        
        # 2. Remove isolated braces, brackets, and leftover symbols
        text = re.sub(r'[\{\}\[\]\\]+', ' ', text)
        
        # 3. Remove excessive punctuation and repeated spaces
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s*([.,:;!?])\s*', r'\1 ', text)

        # 4. Optional: remove email addresses and URLs
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'https?://\S+', '', text)
        
        # 5. Extract from "The present note" onwards
        match = re.search(r'(The present note[\s\S]*)', text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()
        
        return text.strip()
    
## try this after trained the model
# class LatexExtractor:
#     def __init__(self, folder_path, output_path="latex_extracted.json"):
#         self.folder_path = folder_path
#         self.output_path = output_path
#         self.all_files_data = []

#     # CLEAN LATEX COMMANDS
#     def clean_latex(self, text):
#         text = re.sub(r"\\cite\{.*?\}", "", text)
#         text = re.sub(r"\\ref\{.*?\}", "", text)
#         text = re.sub(r"\\[a-zA-Z]+\*", "", text)
#         text = re.sub(r"\\[a-zA-Z]+\{.*?\}", "", text)
#         text = re.sub(r"\\[a-zA-Z]+", "", text)
#         text = text.replace("{", "").replace("}", "")
#         return text

#     def extract_sections_from_file(self, file_path, file_name):

#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read()

#         # --- TITLE ---
#         title_match = re.search(r"\\title\{(.+?)\}", content, re.DOTALL)
#         title = title_match.group(1).strip() if title_match else None

#         # --- AUTHORS ---
#         authors = re.findall(r"\\author\{(.+?)\}", content, re.DOTALL)

#         # --- ABSTRACT ---
#         abstract_match = re.search(r"\\begin\{abstract\}(.+?)\\end\{abstract\}", content, re.DOTALL)
#         abstract = self.clean_latex(abstract_match.group(1).strip()) if abstract_match else ""

#         # --- ALL EQUATIONS (global) ---
#         all_equations = []
#         eq_patterns = [
#             r"\\begin\{equation\}(.+?)\\end\{equation\}",
#             r"\\begin\{align\}(.+?)\\end\{align\}",
#             r"\\\[(.+?)\\\]",
#             r"\$\$(.+?)\$\$",
#             r"\$(.+?)\$"
#         ]

#         for pattern in eq_patterns:
#             all_equations += [eq.strip() for eq in re.findall(pattern, content, re.DOTALL)]

#         # --- SECTIONS ---
#         section_pattern = r"\\section\*?\{(.+?)\}"
#         sec_positions = list(re.finditer(section_pattern, content))

#         sections = []

#         for i, match in enumerate(sec_positions):
#             sec_name = match.group(1).strip()
#             start = match.end()
#             end = sec_positions[i+1].start() if i+1 < len(sec_positions) else len(content)

#             sec_text = content[start:end].strip()
#             sec_clean = self.clean_latex(sec_text)

#             sections.append({
#                 "name": sec_name,
#                 "content": sec_clean
#             })

#         # --- FULL CLEAN TEXT ---
#         full_clean_text = self.clean_latex(content)

#         return {
#             "file_name": file_name,
#             "title": title,
#             "authors": authors,
#             "abstract": abstract,
#             "sections": sections,
#             "equations": all_equations[:10],   # return top 10 eqns
#             "full_text": full_clean_text
#         }

#     def process_all_files(self):
#         for file_name in os.listdir(self.folder_path):
#             if file_name.endswith(".tex"):
#                 file_path = os.path.join(self.folder_path, file_name)
#                 data = self.extract_sections_from_file(file_path, file_name)
#                 self.all_files_data.append(data)

#     def save_to_json(self):
#         with open(self.output_path, "w", encoding="utf-8") as f:
#             json.dump(self.all_files_data, f, indent=2, ensure_ascii=False)

#         print("Saved to", self.output_path)

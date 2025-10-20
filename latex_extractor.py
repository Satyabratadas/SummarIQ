import os
import re
import json
import uuid

class LatexExtractor:
    def __init__(self, folder_path, output_path= "latex_extracted.json"):
        self.folder_path = folder_path
        self.all_files_data = []
        self.output_path = output_path
    
    def extract_sections_from_file(self, file_path, file_name):

        ## """Extract sections, equations, theorems, etc. from a single LaTeX file"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title
        title_match = re.search(r'\\title\s*\{([\s\S]*?)\}', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else None

        # Extract authors (supporting multiple)
        author_pattern = r'\\author(?:\[[^\]]*\])?\{(.+?)\}'
        authors = [a.strip() for a in re.findall(author_pattern, content, re.DOTALL)]

        ## Find all \section{...} labels
        section_pattern = r'\\section\{(.+?)\}(?:\s*\\label\{(.+?)\})?'
        matches = list(re.finditer(section_pattern, content, re.DOTALL))

        sections = []

        for i, match in enumerate(matches):
            sec_name = match.group(1).strip()
            sec_label = match.group(2) if match.group(2) else None
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            sec_content = content[start:end].strip()

            ## Extract key environments
            equations = [eq.strip() for eq in re.findall(r'\\begin\{equation\}(.+?)\\end\{equation\}', sec_content, re.DOTALL)]
            equations += [eq.strip() for eq in re.findall(r'\$\$(.+?)\$\$', sec_content, re.DOTALL)]
            equations += [eq.strip() for eq in re.findall(r'\\\[(.+?)\\\]', sec_content, re.DOTALL)]

            theorems = [t.strip() for t in re.findall(r'\\begin\{theorem\}(.+?)\\end\{theorem\}', sec_content, re.DOTALL)]
            lemmas = [l.strip() for l in re.findall(r'\\begin\{lemma\}(.+?)\\end\{lemma\}', sec_content, re.DOTALL)]
            definitions = [d.strip() for d in re.findall(r'\\begin\{definition\}(.+?)\\end\{definition\}', sec_content, re.DOTALL)]

            sections.append({
                "name": sec_name,
                "label": sec_label,
                "content": sec_content,
                "equations": equations,
                "theorems": theorems,
                "lemmas": lemmas,
                "definitions": definitions
            })

        ## Attach file metadata
        file_id = str(uuid.uuid4())

        return{
            "file_id": file_id,
            "file_name": file_name,
            "authors": authors,
            "title": title,
            "sections": sections
        }



    ## process all .tex files in the given folder
    def process_all_files(self):
        for file_name in os.listdir(self.folder_path):
            if file_name.endswith(".tex"):
                file_path = os.path.join(self.folder_path, file_name)
                file_data = self.extract_sections_from_file(file_path, file_name)
                self.all_files_data.append(file_data)

    ## save the extracted latex data to a json file   
    def save_to_json(self):
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.all_files_data, f, indent=2, ensure_ascii=False)

        print(" Extraction complete! Data saved to latex_extracted.json")

    ## get summary with section wise from the latex file 
    def get_summary(self):
        return [
            {"file_name": f["file_name"], "num_sections": len(f["sections"])}
            for f in self.all_files_data
        ]
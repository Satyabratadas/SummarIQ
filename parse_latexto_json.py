import os
import re
import json
import uuid

folder_path = "/Applications/AI Systems project Data/Traning_latex_files"
all_files_data = []
 

for file_name in os.listdir(folder_path):
    if file_name.endswith(".tex"):
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        section_pattern = r'\\section\{(.+?)\}(?:\s*\\label\{(.+?)\})?'
        matches = list(re.finditer(section_pattern, content, re.DOTALL))

        sections = []
        for i, match in enumerate(matches):
            sec_name = match.group(1).strip()
            sec_label = match.group(2) if match.group(2) else None
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            sec_content = content[start:end].strip()

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

        # file id save with UUID for each each latex file
        file_id = str(uuid.uuid4())

        all_files_data.append({
            "file_id": file_id,
            "file_name": file_name,
            "sections": sections
        })

with open("latex_extracted.json", "w", encoding="utf-8") as f:
    json.dump(all_files_data, f, indent=2, ensure_ascii=False)

print(" Extraction complete! Data saved to latex_extracted.json")

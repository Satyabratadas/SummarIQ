import os
import re
import json

# Folder containing your LaTeX files
folder_path = "/Applications/AI Systems project Data/Traning_latex_files"

# Store results for all files
all_files_data = []

# Loop over each .tex file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith(".tex"):
        file_path = os.path.join(folder_path, file_name)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract sections
        section_pattern = r'\\section\{(.+?)\}(?:\s*\\label\{(.+?)\})?'
        matches = list(re.finditer(section_pattern, content))
        
        sections = []
        for i, match in enumerate(matches):
            sec_name = match.group(1)
            sec_label = match.group(2) if match.group(2) else None
            
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            
            sec_content = content[start:end].strip()
            
            # Extract equations in this section
            equations = re.findall(r'\\begin\{equation\}(.+?)\\end\{equation\}', sec_content, re.DOTALL)
            equations += re.findall(r'\$\$(.+?)\$\$', sec_content, re.DOTALL)
            equations += re.findall(r'\\\[(.+?)\\\]', sec_content, re.DOTALL)
            
            # Extract theorems, lemmas, definitions
            theorems = re.findall(r'\\begin\{theorem\}(.+?)\\end\{theorem\}', sec_content, re.DOTALL)
            lemmas = re.findall(r'\\begin\{lemma\}(.+?)\\end\{lemma\}', sec_content, re.DOTALL)
            definitions = re.findall(r'\\begin\{definition\}(.+?)\\end\{definition\}', sec_content, re.DOTALL)
            
            sections.append({
                "name": sec_name,
                "label": sec_label,
                "content": sec_content,
                "equations": equations,
                "theorems": theorems,
                "lemmas": lemmas,
                "definitions": definitions
            })
        
        all_files_data.append({
            "file_name": file_name,
            "sections": sections
        })

# Save to a JSON file for easy access
with open("latex_extracted.json", "w", encoding="utf-8") as f:
    json.dump(all_files_data, f, indent=2)

print("Extraction complete! Data saved to latex_extracted.json")
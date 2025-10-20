import fitz  # PyMuPDF
from pix2tex.cli import LatexOCR
import os

# Initialize OCR model
model = LatexOCR()

pdf_path = "/Applications/AI Systems project Data/Test_pdf"
# output_tex = "output.tex"
output_tex = "output_tex"
os.makedirs(output_tex, exist_ok=True)

for file_name in os.listdir(pdf_path):
    if not file_name.lower().endswith(".pdf"):
        continue

    pdf_path = os.path.join(pdf_path, file_name)
    base_name = os.path.splitext(file_name)[0]
    output_tex_path = os.path.join(output_tex, f"{base_name}.tex")

    print(f"🔍 Processing: {file_name}")
    doc = fitz.open(pdf_path)
    latex_content = ""

    for page_number, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue

                        # --- Detect Headings ---
                        if span["size"] > 12 and span["flags"] & 2:  # bold heading
                            latex_content += f"\n\\section{{{text}}}\n"
                        else:
                            latex_content += text + " "

        # --- Extract Equation Images ---
        for img_index, img in enumerate(page.get_images(full=True), start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_path = os.path.join(output_tex, f"temp_{base_name}_{page_number}_{img_index}.png")

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            try:
                eq_latex = model(image_path)
                latex_content += f"\n\n$${eq_latex}$$\n\n"
            except Exception as e:
                print(f"⚠️ Equation OCR failed on {file_name} page {page_number}: {e}")

            os.remove(image_path)  # remove temp image

    # --- Save Structured LaTeX File ---
    with open(output_tex_path, "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\n\\usepackage{amsmath}\n\\begin{document}\n")
        f.write(latex_content)
        f.write("\n\\end{document}")

    print(f"✅ Saved: {output_tex_path}\n")

print("🎉 All PDFs converted to structured LaTeX successfully!")

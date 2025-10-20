import fitz
import os
from pix2tex.cli import LatexOCR
from collections import Counter

# page = doc[0]
page_height = 0

ocr = LatexOCR()

pdf_path = "/Applications/AI Systems project Data/Test_pdf"

equation_folder = "equations_images"
os.makedirs(equation_folder, exist_ok=True)

paper_data = {}
current_section = None
eq_counter = 1
all_spans = []
page1_spans = []

for file_name in os.listdir(pdf_path):
    if not file_name.endswith(".pdf"):
        continue

    file_path = os.path.join(pdf_path, file_name)
    doc = fitz.open(file_path)
    page = doc[0]
    page_dict = page.get_text("dict")
    for b in page_dict["blocks"]:
        if b["type"] != 0:
            continue
        for line in b["lines"]:
            for span in line["spans"]:
                page1_spans.append(span)
    print("Total spans found:", len(page1_spans))

    if not page1_spans:
        print("⚠️ No text found on page 1. Skipping.")
        continue

    # --- Get page height for region logic ---
    page_height = page.rect.height

    # --- Focus on top portion of first page ---
    top_spans = [s for s in page1_spans if s["bbox"][1] <= page_height * 0.4]

    if not top_spans:
        print("⚠️ No spans found in top area.")
        continue

    # --- Find dominant font size in top area ---
    font_counter = Counter(round(s["size"], 1) for s in top_spans)
    common_font = font_counter.most_common(1)[0][0]

    # --- Choose spans with font near dominant size ---
    title_candidates = [s for s in top_spans if abs(s["size"] - common_font) < 0.6]

    # --- Sort by Y position (top-down) ---
    title_candidates = sorted(title_candidates, key=lambda s: s["bbox"][1])

    # --- Extract title text ---
    title_text = " ".join(s["text"] for s in title_candidates)
    title_text = title_text.strip()

    if not title_text:
        print("⚠️ Could not detect title text.")
        continue

    print("🧾 Title:", title_text)

    # --- Now detect authors (below title area) ---
    title_bottom = max(s["bbox"][3] for s in title_candidates)
    author_spans = [s for s in page1_spans if title_bottom < s["bbox"][1] < title_bottom + 200]

    authors_text = " ".join(s["text"] for s in author_spans)
    authors_text = authors_text.strip()

    # --- Filter possible author line ---
    if "@" in authors_text or "," in authors_text or " and " in authors_text:
        print("👥 Authors:", authors_text)
    else:
        print("⚠️ Could not confidently find authors.")
import fitz  # PyMuPDF
import os
import json
import re
import hashlib

class PDFExtractor:
    def __init__(self, image_base_folder):
        self.image_base_folder = image_base_folder
        os.makedirs(self.image_base_folder, exist_ok=True)

        # Regex to detect equations
        self.EQUATION_PATTERN = re.compile(
            r"(\b\\frac\b|\\sum|\\int|\\left|\\right|\\sqrt|∑|∫|∞|→|⇒|<=|>=|≪|≫|\bfrac\b|"
            r"[=≠≈≤≥<>]|[0-9]+\s*[=+\-*/^])|(\^[0-9\{])"
        )

    # ------------------------------
    # Remove ID prefix (e.g. 2509.20629v1_) from filename
    # ------------------------------
    def _clean_pdf_name(self, filename):
        name = os.path.splitext(os.path.basename(filename))[0]
        clean_name = re.sub(r"^[0-9v\.]+_", "", name)
        return clean_name + ".pdf"

    # ------------------------------
    # Generate unique filenames for extracted images
    # ------------------------------
    def _unique_filename(self, prefix: str, identifier: str, ext: str = ".png"):
        h = hashlib.sha1(identifier.encode("utf-8")).hexdigest()[:10]
        return f"{prefix}_{h}{ext}"

    # ------------------------------
    # Remove title & author text (only substring, not line)
    # ------------------------------
    def remove_title_author_text(self, text, title="", author=""):
        if not text:
            return text

        lines = text.splitlines()
        first_lines = lines[:10]
        remaining_lines = lines[10:]

        cleaned_first_lines = []
        for line in first_lines:
            clean_line = line
            if title and title.lower() in clean_line.lower():
                clean_line = re.sub(re.escape(title), "", clean_line, flags=re.IGNORECASE)
            if author and author.lower() in clean_line.lower():
                clean_line = re.sub(re.escape(author), "", clean_line, flags=re.IGNORECASE)
            cleaned_first_lines.append(clean_line)

        cleaned_text = "\n".join(cleaned_first_lines + remaining_lines)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()
        return cleaned_text

    # ------------------------------
    # Extract text and equations from one PDF
    # ------------------------------
    def extract_text_and_equations_single(self, pdf_path):
        doc = fitz.open(pdf_path)
        meta = doc.metadata or {}
        title = meta.get("title", "") or ""
        author = meta.get("author", "") or ""

        clean_pdf_name = self._clean_pdf_name(pdf_path)
        pdf_img_folder = os.path.join(self.image_base_folder, os.path.splitext(clean_pdf_name)[0])
        os.makedirs(pdf_img_folder, exist_ok=True)

        full_text_parts = []
        equations = {}
        eq_count = 0

        for pno, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            full_text_parts.append(page_text)

            # Detect equations
            blocks = page.get_text("blocks")
            for block in blocks:
                x0, y0, x1, y1, block_text = block[:5]
                block_text = (block_text or "").strip()
                if not block_text:
                    continue

                if self.EQUATION_PATTERN.search(block_text):
                    eq_count += 1
                    eq_id = f"[EQ{eq_count}]"
                    bbox_id = f"{pdf_path}|page{pno}|{x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}"
                    img_fname = self._unique_filename(f"{os.path.splitext(clean_pdf_name)[0]}_EQ{eq_count}", bbox_id)
                    img_path = os.path.join(pdf_img_folder, img_fname)

                    rect = fitz.Rect(x0, y0, x1, y1)
                    try:
                        pix = page.get_pixmap(clip=rect, dpi=200)
                        pix.save(img_path)
                    except Exception:
                        try:
                            pix = page.get_pixmap(dpi=150)
                            pix.save(img_path)
                        except Exception:
                            img_path = None

                    equations[eq_id] = {
                        "text": block_text,
                        "image_path": img_path
                    }

        raw_text = "\n\n".join(full_text_parts).strip()
        full_text = self.remove_title_author_text(raw_text, title=title, author=author)

        result = {
            "pdf_name": clean_pdf_name,
            "title": title,
            "author": author,
            "text": full_text,
            "equations": equations
        }
        return result

    # ------------------------------
    # Process all PDFs in folder → save as JSON
    # ------------------------------
    def extract_multiple_pdfs_to_json(self, folder_path, output_json_path=None):
        dataset = []

        for fname in sorted(os.listdir(folder_path)):
            if not fname.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(folder_path, fname)
            try:
                res = self.extract_text_and_equations_single(pdf_path)
                dataset.append(res)
                print(f"Processed: {res['pdf_name']}  (Equations found: {len(res['equations'])})")
            except Exception as e:
                print(f"Error processing {fname}: {e}")
                dataset.append({
                    "pdf_name": fname,
                    "error": str(e)
                })

        if output_json_path:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            print(f"✅ JSON dataset saved successfully at: {output_json_path}")

        return dataset


# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    folder_with_pdfs = "/Applications/AI Systems project Data/Test_pdf"
    output_json = "/Users/satyabrata557/Desktop/AI Systems/SummarIQ/pdf_extracted_meta_equations.json"
    image_base = "/Users/satyabrata557/Desktop/AI Systems/SummarIQ/equations_images"

    extractor = PDFExtractor(image_base_folder=image_base)
    dataset = extractor.extract_multiple_pdfs_to_json(folder_with_pdfs, output_json_path=output_json)
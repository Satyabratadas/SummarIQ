import os
import cv2
import json
from pdf2image import convert_from_path
import fitz  # PyMuPDF

# ---------------------------
# 1️⃣ Setup paths
# ---------------------------
PDF_FOLDER = "/Applications/AI Systems project Data/Test_pdf"          # Folder containing PDFs
OUTPUT_FOLDER = "output_batch"
PDF_IMG_FOLDER = os.path.join(OUTPUT_FOLDER, "pdf_pages")
EQUATION_FOLDER = os.path.join(OUTPUT_FOLDER, "equations")
os.makedirs(PDF_IMG_FOLDER, exist_ok=True)
os.makedirs(EQUATION_FOLDER, exist_ok=True)

# ---------------------------
# 2️⃣ Extract text + metadata
# ---------------------------
def extract_text_and_metadata(pdf_path):
    doc = fitz.open(pdf_path)
    meta = doc.metadata or {}
    title = meta.get("title", "") or os.path.splitext(os.path.basename(pdf_path))[0]
    author = meta.get("author", "") or "Unknown"
    
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n\n"
    return full_text.strip(), title, author

# ---------------------------
# 3️⃣ Detect equation regions (image only)
# ---------------------------
def detect_equation_regions(img_path, min_area=500):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w*h > min_area:
            eq_img = img[y:y+h, x:x+w]
            regions.append((eq_img, (x, y, w, h)))
    return regions

# ---------------------------
# 4️⃣ Process all PDFs
# ---------------------------
all_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

for pdf_file in all_pdfs:
    pdf_path = os.path.join(PDF_FOLDER, pdf_file)
    pdf_name = os.path.splitext(pdf_file)[0]

    print(f"Processing: {pdf_file}")

    # 4a. Extract text and metadata
    main_text, title, author = extract_text_and_metadata(pdf_path)

    # 4b. Convert PDF to images
    pdf_pages_folder = os.path.join(PDF_IMG_FOLDER, pdf_name)
    os.makedirs(pdf_pages_folder, exist_ok=True)

    pages = convert_from_path(pdf_path, dpi=200)
    page_img_paths = []
    for i, page in enumerate(pages, start=1):
        img_path = os.path.join(pdf_pages_folder, f"page_{i}.png")
        page.save(img_path, "PNG")
        page_img_paths.append(img_path)

    # 4c. Detect equations & save images
    equations_json = {}
    pdf_equation_folder = os.path.join(EQUATION_FOLDER, pdf_name)
    os.makedirs(pdf_equation_folder, exist_ok=True)

    for page_idx, img_path in enumerate(page_img_paths, start=1):
        eq_regions = detect_equation_regions(img_path)
        for eq_idx, (eq_img, bbox) in enumerate(eq_regions, start=1):
            eq_filename = f"page{page_idx}_EQ{eq_idx}.png"
            eq_path = os.path.join(pdf_equation_folder, eq_filename)
            cv2.imwrite(eq_path, eq_img)
            
            eq_id = f"page{page_idx}_EQ{eq_idx}"
            equations_json[eq_id] = {
                "page": page_idx,
                "bbox": bbox,
                "image_path": eq_path
            }

    # 4d. Save combined JSON per PDF
    data = {
        "pdf_name": pdf_name,
        "title": title,
        "author": author,
        "main_text": main_text,
        "equations": equations_json
    }
    json_path = os.path.join(OUTPUT_FOLDER, f"{pdf_name}_data.json")
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved JSON for {pdf_file} -> {json_path}")

print("✅ All PDFs processed successfully!")

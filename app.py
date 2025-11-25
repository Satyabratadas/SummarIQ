from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from kaggleserver_MLmodel.summarizer_remote import SummarizerRemote
from extractor.latex_extractor import LatexExtractor
import tempfile
import os
from pydantic import BaseModel
from equation_renderer.renderer import latex_to_png_base64
import json


app = FastAPI(
    title="SummarIQ API",
    version="1.0",
    description="AI-powered summarization system for scientific LaTeX research papers."
)

## CORS
app.add_middleware( CORSMiddleware,
    allow_origins=["*"],allow_credentials=True,
    allow_methods=["*"],allow_headers=["*"],
)

## MODEL_PATH = "/content/drive/MyDrive/Summar_IQ_T5Model/t5_large"           ## need to change accordingly

## Load summarizer model ONCE at server startup
summarizer = SummarizerRemote()

## Load LatexExtractor
extractor = LatexExtractor()

# ##   Equation Render API

# class EqModel(BaseModel):
#     latex: str

# @app.post("/render")
# def render(eq: EqModel):
#     img_b64 = latex_to_png_base64(eq.latex)

#     if img_b64 is None:
#         return {
#             "status": "failed",
#             "message": "Rendering failed",
#             "latex": eq.latex
#         }

#     return {
#         "status": "ok",
#         "latex": eq.latex,
#         "image_base64": img_b64
#     }



##   Equation Render function 
def get_equation_image(latex: str):
    """Return raw base64 for a LaTeX equation."""
    return latex_to_png_base64(latex)


## Summarization Endpoint
@app.post("/summarize-latex")
async def summarize_latex(file: UploadFile = File(...)):
    """
    Step 1: User uploads .tex file
    Step 2: Extract LaTeX → JSON (title, authors, sections, equations)
    Step 3: Summarize abstract
    Step 4: Summarize sections
    Step 5: Explain equations
    Step 6: Return FINAL JSON to user
    """

    ## Save uploaded file temporarily

    with tempfile.NamedTemporaryFile(delete=False, suffix=".tex") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    file_name = os.path.basename(tmp_path)

    ## Extract LaTeX content → JSON
    paper = extractor.extract_sections_from_file(tmp_path, file_name)

    final_json = summarizer.summarize(paper)

    important_eqs = final_json.get("important_equations", [])
    enhanced_eqs = []

    for idx, eq_item in enumerate(important_eqs, start=1):

        latex_code = eq_item["equation"]
        raw_b64 = get_equation_image(latex_code)
        enhanced_eqs.append({
            "equation_number": idx,
            "latex": latex_code,
            "raw_image_base64": raw_b64
        })
        
    final_json["important_equations"] = enhanced_eqs

    try:
        os.remove(tmp_path)
    except:
        pass

    return final_json

@app.get("/")
def home():
    return {"status": "OK", "message": "SummarIQ API is running!"}



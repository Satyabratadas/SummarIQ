from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from summarizer.summarizer import Summarizer
from extractor.latex_extractor import LatexExtractor
import tempfile
import os
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

MODEL_PATH = "/content/drive/MyDrive/Summar_IQ_T5Model/t5_large"           ## need to change accordingly

## Load summarizer model ONCE at server startup
summarizer = Summarizer(model_path=MODEL_PATH)

## Load LatexExtractor
extractor = LatexExtractor()

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

    try:
        os.remove(tmp_path)
    except:
        pass

    return final_json

@app.get("/")
def home():
    return {"status": "OK", "message": "SummarIQ API is running!"}



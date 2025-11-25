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

MODEL_PATH = "/content/drive/MyDrive/Summar_IQ_T5Model/t5_large"

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

    final_json = build_summary_json(paper, summarizer)

    # ## Abstract summary
    # abstract_summary = summarizer.summarize_abstract(paper["abstract"])

    # ## Pick top 5 equations
    # top_equations = paper.get("equations", [])[:5]

    # ## Summarize each section
    # section_results = []
    # for sec in paper["sections"]:
    #     section_name = sec["name"]
    #     content = sec["content"]

    #     print("Summarizing section:", section_name)

    #     summary = summarizer.summarize_section(
    #         section_name=section_name,
    #         section_text=content,
    #         important_equations=top_equations
    #     )

    #     section_results.append({
    #         "section_name": section_name,
    #         "summary": summary
    #     })

    # ## Important equations 
    # important_equations_output = []
    # for i, eq in enumerate(top_equations, start=1):
    #     image_base64 = None  # will be replaced by equation renderer

    #     important_equations_output.append({
    #         "equation_no": f"Equation {i}",
    #         "latex": eq,
    #         "image_base64": image_base64
    #     })

    # ## Explain each equation
    # equation_explanations = []
    # for i, eq in enumerate(top_equations, start=1):
    #     explanation_text = summarizer.explain_equation(eq)
    #     image_base64 = important_equations_output[i-1]["image_base64"]

    #     equation_explanations.append({
    #         "equation_no": f"Equation {i}",
    #         "image_base64": image_base64,     # SAME IMAGE INCLUDED
    #         "explanation": explanation_text
    #     })

    # ## JSON OUTPUT
    # final_output = {
    #     "file_name": paper.get("file_name", ""),
    #     "title": paper.get("title", ""),
    #     "authors": paper.get("authors", []),
    #     "abstract_summary": abstract_summary,
    #     "sections": section_results,

    #     "important_equations": important_equations_output,
    #     "equation_explanations": equation_explanations
    # }

    return final_json

@app.get("/")
def home():
    return {"status": "OK", "message": "SummarIQ API is running!"}


def build_summary_json(paper, summarizer):
    ## Abstract summary
    abstract_summary = summarizer.summarize_abstract(paper["abstract"])

    ## Pick top 5 equations
    top_equations = paper.get("equations", [])[:5]

    ## Summarize each section
    section_results = []
    for sec in paper["sections"]:
        section_name = sec["name"]
        content = sec["content"]

        print("Summarizing section:", section_name)

        summary = summarizer.summarize_section(
            section_name=section_name,
            section_text=content,
            important_equations=top_equations
        )

        section_results.append({
            "section_name": section_name,
            "summary": summary
        })

    ## Important equations 
    important_equations_output = []
    for i, eq in enumerate(top_equations, start=1):
        image_base64 = None  # will be replaced by equation renderer

        important_equations_output.append({
            "equation_no": f"Equation {i}",
            "latex": eq,
            "image_base64": image_base64
        })

    ## Explain each equation
    equation_explanations = []
    for i, eq in enumerate(top_equations, start=1):
        explanation_text = summarizer.explain_equation(eq)
        image_base64 = important_equations_output[i-1]["image_base64"]

        equation_explanations.append({
            "equation_no": f"Equation {i}",
            "image_base64": image_base64,     # SAME IMAGE INCLUDED
            "explanation": explanation_text
        })

    ## JSON OUTPUT
    final_output = {
        "file_name": paper.get("file_name", ""),
        "title": paper.get("title", ""),
        "authors": paper.get("authors", []),
        "abstract_summary": abstract_summary,
        "sections": section_results,

        "important_equations": important_equations_output,
        "equation_explanations": equation_explanations
    }

    return final_output
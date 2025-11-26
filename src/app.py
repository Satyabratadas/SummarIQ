from fastapi import FastAPI, UploadFile, File, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from models.summarizer_remote import SummarizerRemote
from prometheus_client import Counter, Histogram, generate_latest, Gauge
# from summarizer_local import SummarizerLocal
from extractor.latex_extractor import LatexExtractor
import tempfile
import os
from pydantic import BaseModel
from equation_renderer.renderer import latex_to_png_base64
import time
import json
import gradio as gr

class FeedbackModel(BaseModel):
    name: str | None = None
    rating: int
    comments: str | None = None

PREDICTION_COUNTER = Counter(
    "summariq_request_count",
    "Total number of requests to SummarIQ API",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "summariq_request_latency_seconds",
    "Latency of SummarIQ API requests",
    ["endpoint"]
)


# FEEDBACK METRICS
FEEDBACK_COUNT = Counter(
    "summariq_feedback_total",
    "Total number of user feedback submissions"
)

FEEDBACK_RATING_HIST = Histogram(
    "summariq_feedback_rating",
    "Distribution of feedback ratings",
    buckets=[1, 2, 3, 4, 5]
)

LAST_FEEDBACK_RATING = Gauge(
    "summariq_feedback_latest_rating",
    "Most recent rating submitted by a user"
)

FEEDBACK_WITH_COMMENTS = Counter(
    "summariq_feedback_with_comments_total",
    "Total feedback entries containing comments"
)

FEEDBACK_NO_COMMENTS = Counter(
    "summariq_feedback_no_comments_total",
    "Total feedback entries without comments"
)


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

## Load summarizer remote model from kaggle ONCE at server startup
summarizer = SummarizerRemote()

## Load summarizer local model ONCE at server startup
# summarizer = SummarizerLocal(model_name="t5-small")

## Load LatexExtractor
extractor = LatexExtractor()


##   Equation Render function 
def get_equation_image(latex: str):
    """Return raw base64 for a LaTeX equation."""
    return latex_to_png_base64(latex)

##   Prometheus Metrics calculate
@app.middleware("http")
async def prometheus_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    REQUEST_LATENCY.labels(request.url.path).observe(process_time)
    PREDICTION_COUNTER.labels(request.method, request.url.path, response.status_code).inc()

    return response

@app.post("/feedback")
async def feedback_endpoint(fb: FeedbackModel):

    # Update Prometheus metrics
    FEEDBACK_COUNT.inc()
    FEEDBACK_RATING_HIST.observe(fb.rating)
    LAST_FEEDBACK_RATING.set(fb.rating)

    if fb.comments and fb.comments.strip():
        FEEDBACK_WITH_COMMENTS.inc()
    else:
        FEEDBACK_NO_COMMENTS.inc()

    return {"status": "ok", "msg": "Feedback recorded"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")


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



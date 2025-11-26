from fastapi import FastAPI
from pydantic import BaseModel
from renderer import latex_to_png_base64

app = FastAPI(title="Equation Renderer Service")

class EqModel(BaseModel):
    latex: str

@app.post("/render")
def render(eq: EqModel):
    img_b64 = latex_to_png_base64(eq.latex)

    if img_b64 is None:
        return {"status": "failed", "message": "Rendering failed", "latex": eq.latex}

    return {
        "status": "ok",
        "image_base64": img_b64,
        "latex": eq.latex
    }
@app.get("/")
def home():
    return {"status": "renderer running", "message": "Equation Renderer API is online."}
import requests
import gradio as gr

FASTAPI_URL = "http://summar_api:8000/summarize-latex"

def summarize_via_api(file_path):
    # file_path is a string, NOT a file object
    # So we must open it manually
    with open(file_path, "rb") as f:
        files = {"file": ("uploaded.tex", f, "application/octet-stream")}
        response = requests.post(FASTAPI_URL, files=files)

    if response.status_code != 200:
        return {"error": f"FastAPI returned status {response.status_code}"}

    return response.json()

ui = gr.Interface(
    fn=summarize_via_api,
    inputs=gr.File(label="Upload LaTeX File (.tex)"),
    outputs="json",
    title="SummarIQ – Gradio UI",
    description="Upload a LaTeX file to generate summary using FastAPI backend."
)

ui.launch(server_name="0.0.0.0", server_port=7860)



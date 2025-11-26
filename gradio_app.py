# import requests
# import gradio as gr
# import base64
# from PIL import Image
# import io

# FASTAPI_URL = "http://summar_api:8000/summarize-latex"

# # Helper to convert base64 → Image
# def base64_to_image(b64):
#     img_bytes = base64.b64decode(b64)
#     return Image.open(io.BytesIO(img_bytes))


# # Fully stable handler — works with ALL Gradio versions
# def summarize_via_api(file_obj):

#     # If Gradio gives a file path (string)
#     if isinstance(file_obj, str):
#         with open(file_obj, "rb") as f:
#             files = {"file": ("uploaded.tex", f, "application/octet-stream")}
#             response = requests.post(FASTAPI_URL, files=files)

#     # If Gradio gives a TemporaryFileWrapper / file object
#     else:
#         file_obj.seek(0)
#         files = {"file": ("uploaded.tex", file_obj, "application/octet-stream")}
#         response = requests.post(FASTAPI_URL, files=files)

#     # Error handling
#     if response.status_code != 200:
#         return f"Error from backend: {response.status_code}", None

#     data = response.json()

#     # Build readable HTML
#     title = data.get("title", "")
#     authors = ", ".join(data.get("authors", []))
#     abs_sum = data.get("abstract_summary", "")

#     html = f"""
#     <h2>{title}</h2>
#     <p><b>Authors:</b> {authors}</p>
#     <h3>Abstract Summary</h3>
#     <p>{abs_sum}</p>
#     <hr/>
#     """

#     # Sections
#     html += "<h3>Section Summaries</h3>"
#     for sec in data.get("sections", []):
#         html += f"<h4>{sec['section_name']}</h4><p>{sec['section_summary']}</p>"

#     # Equations
#     html += "<h3>Important Equations</h3>"
#     images = []

#     for eq in data.get("important_equations", []):
#         latex = eq.get("latex") or eq.get("equation")
#         html += f"<p><b>{eq['equation_number']}</b>: {latex}</p>"

#         b64 = eq.get("raw_image_base64")
#         if b64:
#             images.append(base64_to_image(b64))

#     return html, images


# # SIMPLE Gradio layout — guaranteed to work
# with gr.Blocks() as demo:
#     gr.Markdown("# SummarIQ – Summarizer UI")

#     file = gr.File(label="Upload LaTeX (.tex)")
#     html_output = gr.HTML()
#     img_output = gr.Gallery()

#     submit = gr.Button("Summarize")
#     submit.click(summarize_via_api, file, [html_output, img_output])

# demo.launch(server_name="0.0.0.0", server_port=7860)




import requests
import gradio as gr
import base64
from PIL import Image
import io
import json
import os

FASTAPI_URL = "http://summar_api:8000/summarize-latex"
FEEDBACK_FILE = "feedback_store.json"


# Helper: ensure feedback file exists
def init_feedback_file():
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w") as f:
            json.dump([], f)


def save_feedback(name, rating, comments):
    init_feedback_file()

    entry = {
        "name": name,
        "rating": rating,
        "comments": comments
    }

    with open(FEEDBACK_FILE, "r") as f:
        data = json.load(f)

    data.append(entry)

    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return "✅ Thank you! Your feedback has been recorded."


# Convert base64 → image
def base64_to_image(b64):
    img_bytes = base64.b64decode(b64)
    return Image.open(io.BytesIO(img_bytes))


# Summarizer function
def summarize_via_api(file_obj):
    if isinstance(file_obj, str):
        with open(file_obj, "rb") as f:
            files = {"file": ("uploaded.tex", f, "application/octet-stream")}
            response = requests.post(FASTAPI_URL, files=files)
    else:
        file_obj.seek(0)
        files = {"file": ("uploaded.tex", file_obj, "application/octet-stream")}
        response = requests.post(FASTAPI_URL, files=files)

    if response.status_code != 200:
        return f"Error from backend: {response.status_code}", None

    data = response.json()

    title = data.get("title", "")
    authors = ", ".join(data.get("authors", []))
    abs_sum = data.get("abstract_summary", "")

    html = f"""
    <h2>{title}</h2>
    <p><b>Authors:</b> {authors}</p>
    <h3>Abstract Summary</h3>
    <p>{abs_sum}</p>
    <hr/>
    """

    html += "<h3>Section Summaries</h3>"
    for sec in data.get("sections", []):
        html += f"<h4>{sec['section_name']}</h4><p>{sec['section_summary']}</p>"

    html += "<h3>Important Equations</h3>"
    images = []

    for eq in data.get("important_equations", []):
        latex = eq.get("latex") or eq.get("equation")
        html += f"<p><b>{eq['equation_number']}</b>: {latex}</p>"

        b64 = eq.get("raw_image_base64")
        if b64:
            images.append(base64_to_image(b64))

    return html, images


# ===============================
#        GRADIO UI LAYOUT
# ===============================
with gr.Blocks() as demo:
    
    gr.Markdown("# 📘 SummarIQ – LaTeX Summarizer & Feedback UI")

    with gr.Tabs():

        # -------------------- TAB 1 — SUMMARIZER --------------------
        with gr.Tab("Summarizer"):

            file = gr.File(label="Upload LaTeX (.tex)")
            html_output = gr.HTML()
            img_output = gr.Gallery()
            submit = gr.Button("Summarize")

            submit.click(
                summarize_via_api,
                inputs=file,
                outputs=[html_output, img_output]
            )

        # -------------------- TAB 2 — FEEDBACK ----------------------
        with gr.Tab("Feedback"):

            gr.Markdown("### 📝 Share Your Experience With SummarIQ")

            name = gr.Textbox(label="Your Name (optional)")
            rating = gr.Slider(minimum=1, maximum=5, step=1, label="Rate the Summarizer (1 - 5)")
            comments = gr.Textbox(label="Feedback", lines=5, placeholder="Write your thoughts...")

            submit_fb = gr.Button("Submit Feedback")
            fb_response = gr.HTML()

            submit_fb.click(
                save_feedback,
                inputs=[name, rating, comments],
                outputs=fb_response
            )


demo.launch(server_name="0.0.0.0", server_port=7860)

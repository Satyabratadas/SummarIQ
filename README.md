## 🚀 **SummarIQ – AI-Powered Scientific Paper Summarizer**
**Extract** • **Understand** • **Summarize** • **Visualize (PDF + LaTeX)**
SummarIQ is an AI-powered system designed to summarize scientific research papers written in PDF or LaTeX. It extracts sections, equations, metadata, and produces structured summaries using transformer-based models like **T5-small** and **BART-large**.

This project includes:

-  **AI summarization models (T5, BART)**
-  **LaTeX equation extraction & rendering**
-  **FastAPI backend**
-  **Gradio UI**
-  **Docker deployment**
-  **Prometheus + Grafana monitoring**
-  **iOS UI prototypes**
-  **Remote GPU inference (Kaggle)**

---

## 🎥 System Demo Video

Watch the system in action:

[[![Watch the demo](https://img.youtube.com/vi/s3JzzzPyIjI/maxresdefault.jpg)](https://youtu.be/s3JzzzPyIjI)]

---

## Project Structure
```
├── App design
│   ├── Purple Pink Gradient Login Page Mobile Prototype (3)
│   │   ├── 1.jpg
│   │   ├── 2.jpg
│   │   └── 3.jpg
│   ├── Screen_1.png
│   ├── Screen_2.png
│   └── Screen_3.png
├── deployment
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── gradio_app.py
├── documentation
│   ├── plot_images
│   │   ├── Architechture_diagram.png
│   │   ├── fairness_explainability.png
│   │   ├── githubrepo.png
│   │   ├── sample_equation_output.png
│   │   ├── sample_summary_output.png
│   │   └── shap_summary.png
│   ├── Poster.pdf
│   ├── Project_report.pdf
│   └── SummarIQ_project_template.pdf
├── monitoring
│   ├── grafana
│   │   └── summariq_graphana_dashboard.json
│   ├── metrices_report
│   │   ├── metrics_report_valset.csv
│   │   ├── monitoring_images
│   │   │   ├── cpu_usage.png
│   │   │   ├── Fairlear_matrices.png
│   │   │   ├── feedback_latest_rating.png
│   │   │   ├── feedback_no_comments_total.png
│   │   │   ├── feedback_rating.png
│   │   │   ├── feedback_total.png
│   │   │   ├── feedback_with_comments_total.png
│   │   │   ├── localhost_metrices_log.png
│   │   │   ├── request_count.png
│   │   │   ├── request_latency_seconds.png
│   │   │   └── shap_values.png
│   │   └── structured_summary.csv
│   └── prometheus
│       ├── alert_rules.yml
│       └── prometheus.yml
├── Notebooks
│   ├── bart_train.ipynb
│   ├── kaggle_server_run.ipynb
│   ├── risk_management.ipynb
│   ├── t5_model_test.ipynb
│   ├── test_summarize.ipynb
│   ├── test_t5_small.ipynb
│   ├── training.ipynb
│   └── valset_test.ipynb
├── README.md
├── requirements_projects.txt
├── requirements.txt
├── src
    ├── __pycache__
    │   └── app.cpython-310.pyc
    ├── app.py
    ├── data
    │   ├── latex_extracted.json
    │   └── Test_pdf
    │       ├── 2404.08534v2.pdf
    │       ├── sm.pdf
    │       ├── sm.tex
    │       ├── Tower_V3.tex
    │       └── tower.pdf
    ├── equation_renderer
    │   ├── __pycache__
    │   │   ├── app.cpython-310.pyc
    │   │   ├── eqapp.cpython-310.pyc
    │   │   ├── quicklatex_app.cpython-310.pyc
    │   │   ├── quicklatex_renderer.cpython-310.pyc
    │   │   └── renderer.cpython-310.pyc
    │   ├── eqapp.py
    │   └── renderer.py
    ├── extractor
    │   ├── __pycache__
    │   │   └── latex_extractor.cpython-310.pyc
    │   ├── extract_usingcv.py
    │   └── latex_extractor.py
    ├── models
    │   ├── __pycache__
    │   │   └── summarizer_remote.cpython-310.pyc
    │   └── summarizer_remote.py
    ├── summarizer_kaggle.py
    ├── summarizer_local.py
    └── utils
        ├── load_data.py
        └── response_server
            ├── api_response.json
            └── response_without_T5server.json

```

## Features

### AI Summarization

- T5-small (fast, lightweight)
- BART-large (high accuracy)
- Section-wise summarization
- Handles long scientific text

### LaTeX Equation Handling

- Detects inline & block equations
- Renders equations as images
- Ranks important equations

### FastAPI Backend

- ```/summarize-latex``` endpoint
- PDF/LaTeX processing
- JSON structured output

### Gradio UI

- Upload interface
- Real-time response
- Feedback collection

### Deployment

- Dockerfile + docker-compose
- Separate services for API, Gradio, Prometheus
- Works on local + cloud environments

### Monitoring

- Prometheus for metric scraping
- Grafana dashboards
- Custom metric: ```summariq_feedback_total```

### iOS Mobile App Prototype
- Screens included in ```App design/```
- Designed for future live deployment

## Installation
### 1. Clone the repository
```
git clone https://github.com/yourusername/SummarIQ.git
cd SummarIQ
```
### 2.Create a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
This project uses two separate requirements files:

- #### requirements_projects.txt(local development)
  ```
  pip install -r requirements_projects.txt
  ```
- #### requirements.txt(Docker/production)
  ```
  pip install -r requirements.txt
  ```
## Run with Docker
- #### Build containers
  ```
  docker-compose build
  ```
- #### Start services
  ```
  docker-compose up
  ```
This starts:
- **FastAPI** → http://localhost:8000
- **Gradio UI** → http://localhost:7860
- **Prometheus** → http://localhost:9090
- **Grafana** → http://localhost:3000

## Run Locally (without Docker)
### Start FastAPI server
```
uvicorn app:app --reload --port 8000
```
## Start Gradio UI
```
python gradio_app.py
```

## API Usage
### Endpoint
```
POST /summarize-latex
```
### Example (cURL)
```
curl -X POST -F "file=@sample.tex" http://localhost:8000/summarize-latex
```
### Output Example
```
utils/response_server/api_response.json
```

## Model Pipeline

- Receive LaTeX/PDF
- Extract sections & equations
- Preprocess scientific text
- Summarize using T5/BART
- Produce structured JSON output
- Render LaTeX equations
- Display summary in Gradio / iOS UI

## Monitoring (Prometheus + Grafana)
Metrics collected:
- API latency (p50, p90, p95)
- Total requests
- Feedback count ```summariq_feedback_total```
- CPU/RAM usage
- Docker container performance
- Error rates
Dashboards:
- Grafana → http://localhost:3000
- Prometheus → http://localhost:9090

## iOS App Prototype
Located in ```App design/```:
Includes:
- Login screen
- Upload screen
- Processing screen
- Summary UI design
Powered by SwiftUI (planned for Phase 2 deployment).

## Roadmap
**Phase 2**
- Fine-tuned summarization (domain-specific)
- Full iOS app integration
- Deploy backend to AWS/GCP
- Real-time feedback storage in DB (MongoDB/PostgreSQL)
- Advanced Grafana dashboards
- Semantic equation understanding
- User accounts + authentication
  



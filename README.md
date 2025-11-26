## 🚀 **SummarIQ – AI-Powered Scientific Paper Summarizer**
**Extract** • **Understand** • **Summarize** • **Visualize (PDF + LaTeX)**
SummarIQ is an AI-powered system designed to summarize scientific research papers written in PDF or LaTeX. It extracts sections, equations, metadata, and produces structured summaries using transformer-based models like **T5-small** and **BART-large**.

This project includes:

- 🧠 **AI summarization models (T5, BART)**
- 📄 **LaTeX equation extraction & rendering**
- ⚙️ **FastAPI backend**
- 🖥️ **Gradio UI**
- 🐳 **Docker deployment**
- 📊 **Prometheus + Grafana monitoring**
- 📱 **iOS UI prototypes**
- ☁️ **Remote GPU inference (Kaggle)**

## 🎥 **System Demo Video (Google Drive)**

Since GitHub does not allow uploading large .mov files, the demo video is hosted on Google Drive:
🔗 Demo Video: [https://drive.google.com/your-video-link](https://drive.google.com/file/d/1Ei_goGmW-2tYrxa5s9L3yhcWSFytvwmk/view?usp=drive_link)

## 📁 **Project Structure**

```
├── App design
│   ├── Purple Pink Gradient Login Page Mobile Prototype (3)
│   │   ├── 1.jpg
│   │   ├── 2.jpg
│   │   └── 3.jpg
│   ├── Screen_1.png
│   ├── Screen_2.png
│   └── Screen_3.png
├── Notebooks
│   ├── bart_train.ipynb
│   ├── kaggle_server_run.ipynb
│   ├── t5_model_test.ipynb
│   ├── test_summarize.ipynb
│   ├── test_t5_small.ipynb
│   ├── training.ipynb
│   └── valset_test.ipynb
├── deployment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── gradio_app.py
├── documentation
│   ├── Elevator Pitch.pdf
│   ├── README.md
│   └── SummarIQ.pdf
├── monitoring
│   ├── grafana
│   ├── metrices_report
│   │   ├── metrics_report_valset.csv
│   │   └── structured_summary.csv
│   └── prometheus
│       └── prometheus.yml
├── requirements.txt
├── requirements_projects.txt
├── src
│   ├── app.py
│   ├── data
│   │   ├── Test_pdf
│   │   │   ├── 2404.08534v2.pdf
│   │   │   └── sm.tex
│   │   └── latex_extracted.json
│   ├── equation_renderer
│   │   ├── eqapp.py
│   │   └── renderer.py
│   ├── extractor
│   │   ├── extract_usingcv.py
│   │   └── latex_extractor.py
│   ├── models
│   │   └── summarizer_remote.py
│   ├── summarizer_kaggle.py
│   ├── summarizer_local.py
│   └── utils
│       ├── load_data.py
│       └── response_server
│           ├── api_response.json
│           └── response_without_T5server.json
└── videos
    └── Screen Recording 2025-11-26 at 6.27.09 AM.mov
```
## ✨ Features

### 🔍 AI Summarization

- T5-small (fast, lightweight)
- BART-large (high accuracy)
- Section-wise summarization
- Handles long scientific text

### 🧮 LaTeX Equation Handling

- Detects inline & block equations
- Renders equations as images
- Ranks important equations

### ⚙️ FastAPI Backend

- ```/summarize-latex``` endpoint
- PDF/LaTeX processing
- JSON structured output

### 🖥️ Gradio UI

- Upload interface
- Real-time response
- Feedback collection

### 🐳 Deployment

- Dockerfile + docker-compose
- Separate services for API, Gradio, Prometheus
- Works on local + cloud environments

### 📊 Monitoring

- Prometheus for metric scraping
- Grafana dashboards
- Custom metric: ```summariq_feedback_total```

### 📱 iOS Mobile App Prototype
- Screens included in ```App design/```
- Designed for future live deployment

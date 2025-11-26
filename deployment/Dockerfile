FROM python:3.10-slim

WORKDIR /app

# -----------------------------
# Install OS dependencies
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libopenblas-dev \
    texlive-latex-extra \
    texlive-fonts-recommended \
    dvipng \
    ghostscript \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install PyTorch (CPU-only)
# -----------------------------
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch

# -----------------------------
# Install required Python libraries
# -----------------------------
RUN pip install --no-cache-dir \
    numpy \
    transformers \
    sentencepiece \
    fastapi \
    uvicorn \
    python-multipart \
    prometheus_client \
    gradio

# Copy src folder
COPY src /app/src

# Copy deployment folder
COPY deployment /app/deployment

COPY requirements.txt /app/requirements.txt

# Python path so imports work
ENV PYTHONPATH="/app/src"

# -----------------------------
# Expose API port
# -----------------------------
EXPOSE 8000

# -----------------------------
# Start FastAPI server
# -----------------------------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]









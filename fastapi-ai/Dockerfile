FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel

WORKDIR /smartbow

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./fastapi-ai/app ./app


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libreoffice \
    libxml2-dev \
    libxslt-dev \
    tesseract-ocr \
    tesseract-ocr\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY services/extractor /app
COPY shared /app/shared

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/shared"
CMD ["python", "main.py"]

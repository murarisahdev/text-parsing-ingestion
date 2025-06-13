# Text Parsing Ingestion Pipeline

A **modular**, **scalable**, and **event-driven** document ingestion pipeline built with **FastAPI**, **Python**, **Docker**, and **Google Cloud Pub/Sub**. Designed for use cases like **RAG**, **semantic search**, and **LLM preprocessing**.

---

## Architecture Overview

```text
[ Ingestion API ] ──> [ Pub/Sub Topic ] ──> [ Extractor Service ]
        │                        │                      │
        ▼                        ▼                      ▼
  File / URL Input        Smart Parsing        GCS Upload + Pub/Sub
```

---

## Project Structure

```text
text-parsing-ingestion-pipeline/
│
├── docs/                         # Project documentation
│   └── README.md
│
├── services/                     # Microservices
│   ├── extractor/                # Extracts & parses document/URL text
│   │   ├── keys/
│   │   ├── utils/
│   │   ├── __init__.py
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   ├── parsing_text_api/        # FastAPI-based ingestion endpoint
│   │   ├── keys/
│   │   ├── utils/
│   │   ├── api.py
│   │   ├── credentials.json
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── pubsub_client.py
│   │   └── requirements.txt
│
├── shared/                      # Shared code across services
│   ├── handlers/
│   ├── pubsub/
│   │   ├── publisher.py
│   │   └── subscriber.py
│   │
│   └── storage/
│       ├── file_utils.py
│       └── gcs_client.py
│
├── terraform/                   # (Optional) IaC using Terraform
│
├── .env                         # Environment variables
├── .flake8                      # Linter config
├── .gitignore
├── docker-compose.yml           # Local orchestration
├── pyproject.toml               # Formatter & tool config
├── config.py                    # Centralized config
├── credentials.json             # GCP credentials (local only)
├── .pre-commit-config.yaml      # Pre-commit hooks
└── parsing-text-*.json          # Temporary or output metadata
```

---

## Features

- Ingest **PDF**, **HTML**, **scanned images**, and **URLs**
- Built with **FastAPI**, **Pub/Sub**, **Docker**, **GCS**
- Multi-tenant support and bucket isolation
- Smart chunking for LLM preprocessing
- Modular design with clean microservices
- Designed for **RAG pipelines**, **embedding**, and **indexing**

---

## Configuration

- All configs are handled via `.env` and `config.py`
- GCP credentials are securely loaded from a service account file
- You can configure:
  - Chunk size and overlap
  - Retry mechanisms
  - Pub/Sub topics and subscriptions
  - Bucket names per tenant

---

## Parsing Strategy

Text extraction is done with a hybrid parsing approach:

| Source Type | Library/Tool Used         | Notes |
|-------------|----------------------------|-------|
| PDFs        | `PyMuPDF`, `pdfplumber`    | Fallback to OCR for scanned |
| Images      | `Tesseract OCR`            | Uses Google Vision API optionally |
| HTML/URLs   | `BeautifulSoup`, `Playwright` | Smart HTML cleanup |
| Any file    | `unstructured` (optional)  | Layout-aware parsing |

Parsed text is saved as `.json` in **GCS**, then forwarded for chunking or embedding.

---

## API Usage

### Upload File

```bash
curl -X POST http://13.201.224.92:8000/api/upload   -F "tenant_id=tenant1"   -F "file=@/path/to/document.pdf"
```

### Submit URL

```bash
curl -X POST http://13.201.224.92:8000/api/url   -H "Content-Type: application/x-www-form-urlencoded"   -d "tenant_id=tenant1&url=https://example.com"
```

### Swagger Docs

Visit: `http://13.201.224.92:8000/docs`

---

## Local Development

### 1. Clone the repo

```bash
git clone https://github.com/murarisahdev/text-parsing-ingestion.git
cd text-parsing-ingestion
```

### 2. Configure environment

- Copy `.example-env` to `.env` and fill in values.
- Add your GCP credentials as `credentials.json`.

```bash
export GOOGLE_APPLICATION_CREDENTIALS="./credentials.json"
```

### 3. Start services

```bash
docker-compose up --build
```

---

##  GCP Deployment

1. Create Pub/Sub topics and subscriptions
2. Set up Cloud Storage bucket(s)
3. Deploy services to Cloud Run or GKE
4. Make bucket objects publicly viewable if testing external access:

```python
from google.cloud import storage
def make_blob_public(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.make_public()
    return blob.public_url
```

---

## Estimated Cost (1,000 docs)

| Component         | Cost (USD) | Notes |
|------------------|------------|-------|
| GCS              | ~$0.02     | 1GB storage & PUT |
| Pub/Sub          | ~$0.10     | Mostly within free tier |
| Cloud Run        | ~$1.00     | Depends on CPU/memory |
| Vision OCR       | ~$1.50     | Only if used |
| **Total**        | **~$2.62** | May be zero on free tier |

---

## Development Tips

```bash
# Clean & rebuild services
docker-compose down
docker-compose up --build

# Format/lint
ruff check .
```

---

##  Related

- [Google Cloud Pub/Sub](https://cloud.google.com/pubsub)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [unstructured.io](https://github.com/Unstructured-IO/unstructured)
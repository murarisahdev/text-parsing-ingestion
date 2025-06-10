# Text Parsing Ingestion Pipeline

A scalable, event-driven document ingestion pipeline for Google Cloud.  
**Features:** Multi-tenant, microservices, chunking, embedding, OCR, and vector storage.

---

## Architecture

**Microservices:**
- **ingestion_api:** HTTP API for file/URL ingestion, authentication, and event publishing (Pub/Sub).
- **extractor:** Consumes events, extracts text (with OCR), chunks, and sends to embedding/vector DB.
- **shared:** Common utilities and code.
- **terraform:** (Optional) Infrastructure as Code for GCP resources.

**Flow:**
1. Client uploads file or URL to `ingestion_api`.
2. API authenticates, publishes event to Pub/Sub.
3. `extractor` service processes event: downloads, extracts, chunks, embeds, and stores results.
4. Extracted files go to GCS; vectors to vector DB; metadata tracked.

---

## Project Structure

```
.
├── docs/                  # Documentation
├── services/
│   ├── extractor/         # Extraction & chunking service
│   │   ├── extractor.py
│   │   ├── main.py
│   │   ├── utils/
│   │   └── ...
│   └── ingestion_api/     # HTTP API & Pub/Sub parsing_text_api
│       ├── api.py
│       ├── main.py
│       ├── pubsub_client.py
│       ├── utils.py
│       └── ...
├── shared/                # Shared code
├── terraform/             # (Optional) IaC scripts
├── docker-compose.yml     # Local orchestration
├── .env                   # Environment variables
├── config.py              # Project config
├── requirements.txt       # Root dependencies
└── README.md
```

---

## Setup & Deployment

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- GCP account (Pub/Sub, GCS, Vision API, etc.)
- (Optional) Terraform

### Local Development

1. **Clone the repo:**
    ```sh
    git clone https://github.com/murarisahdev/text-parsing-ingestion.git
    cd text-parsing-ingestion-pipeline
    ```

2. **Configure environment:**
    - Copy `.env.example` to `.env` and fill in values.
    - Place GCP credentials in `credentials.json`.

3. **Build & run services:**
    ```sh
    docker-compose up --build
    ```

## Example Usage

### Ingest a File

```sh
curl -X 'POST' \
  'http://0.0.0.0:8000/api/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'tenant_id=test1' \
  -F 'file=path/to/document.pdf;type=application/pdf'
```

### Ingest a Web Page

```sh
curl -X 'POST' \
  'http://0.0.0.0:8000/api/url' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'tenant_id=test1&url=example.com/page'

---

## Configuration

- All config via `.env` or environment variables.
- No hard-coded credentials.
- Chunking, embedding, and storage are configurable.

---

---

## Cost Estimate (per 1,000 docs)

| Component         | Est. Cost (USD) | Notes                                      |
|-------------------|-----------------|---------------------------------------------|
| Cloud Storage     | $0.02           | 1GB storage, 1,000 PUT ops                  |
| Pub/Sub           | $0.10           | 1,000,000 messages (free tier covers most)  |
| Cloud Run         | $1.00           | 1,000 doc processing (light CPU/mem)        |
| Vision API (OCR)  | $1.50           | 1,000 pages (if OCR used)                   |         |
| **Total**         | **~$2.62**      | Excluding free tier, depends on usage       |

---

## Design Choices

- **Microservices:** Scalability, modularity, and clear separation of concerns.
- **Event-driven:** Pub/Sub for decoupling and reliability.
- **Multi-tenancy:** Per-tenant buckets/namespaces.
- **Observability:** Structured logs, metrics, error handling.
- **Security:** API key/OAuth, tenant isolation.
- **Extensible:** Easy to add new file types, embedding models, or storage backends.


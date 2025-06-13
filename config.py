# config.py
import os

from dotenv import load_dotenv

load_dotenv()


GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", "parsing-text-563777956a4b.json"
)
GCP_PROJECT = os.getenv("GCP_PROJECT", "parsing-text")
GCS_BUCKET = os.getenv("GCS_BUCKET", "parsing-text-bucket")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "text-parsing-ingestion-request")
SUBSCRIPTION_NAME = os.getenv("SUBSCRIPTION_NAME", "extractor-sub")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET", "extracted-output")

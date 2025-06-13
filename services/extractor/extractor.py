import logging
import tempfile

from config import PUBSUB_TOPIC
from services.extractor.utils.text_extractors import (smart_pdf_parser,
                                                      smart_url_parser)
from shared.pubsub.publisher import publish_event
from shared.storage.gcs_client import (download_file_from_gcs,
                                       upload_extrected_text_output_bucket)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def extract_text_from_pdf(path: str, from_gcs: bool = True) -> str:
    try:
        if from_gcs:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                download_file_from_gcs(path, tmp_file.name)
                return smart_pdf_parser(tmp_file.name)
        else:
            return smart_pdf_parser(path)
    except Exception as e:
        logger.error("PDF extraction failed: %s", e, exc_info=True)
        return ""


def extract_text_from_url(url: str) -> str:
    try:
        return smart_url_parser(url)
    except Exception as e:
        logger.error("URL extraction failed: %s", e, exc_info=True)
        return ""


def handle_ingestion_event(message_dict: dict):
    try:
        logger.info("Received message: %s", message_dict)
        msg_type = message_dict.get("type")

        if not msg_type:
            logger.error("Missing 'type' in message: %s", message_dict)
            return

        if msg_type == "url":
            tenant_id = message_dict.get("tenant_id")
            url_id = message_dict.get("url_id")
            url = message_dict.get("url")

            if not all([tenant_id, url_id, url]):
                logger.error("Missing required fields in URL message: %s", message_dict)
                return

            logger.info("Processing URL: %s for tenant %s with ID %s", url, tenant_id, url_id)
            text = extract_text_from_url(url)
            logger.info("Extracted text (first 100 chars): %s", text[:100])

            gcs_blob_name = f"url/{url_id}.json"
            public_url = upload_extrected_text_output_bucket(
                gcs_blob_name,
                {
                    "tenant_id": tenant_id,
                    "document_id": url_id,
                    "source": "url",
                    "url": url,
                    "text": text,
                },
            )

            publish_event(
                PUBSUB_TOPIC,
                {
                    "document_id": url_id,
                    "text": text,
                    "tenant_id": tenant_id,
                    "filename": url,
                    "extracted_gcs_url": public_url,
                },
            )

            logger.info("URL extraction completed and event published.")

        elif msg_type == "file":
            tenant_id = message_dict.get("tenant_id")
            file_id = message_dict.get("file_id")
            gcs_path = message_dict.get("gcs_path")

            if not all([tenant_id, file_id, gcs_path]):
                logger.error("Missing required fields in file message: %s", message_dict)
                return

            logger.info("Processing file %s for tenant %s with ID %s", gcs_path, tenant_id, file_id)
            text = extract_text_from_pdf(gcs_path)
            logger.info("Extracted text (first 100 chars): %s", text[:100])

            gcs_blob_name = f"file/{file_id}.json"
            public_url = upload_extrected_text_output_bucket(
                gcs_blob_name,
                {
                    "tenant_id": tenant_id,
                    "document_id": file_id,
                    "source": "file",
                    "gcs_path": gcs_path,
                    "text": text,
                },
            )

            publish_event(
                PUBSUB_TOPIC,
                {
                    "document_id": file_id,
                    "text": text,
                    "tenant_id": tenant_id,
                    "filename": message_dict.get("filename"),
                    "extracted_gcs_url": public_url,
                },
            )

            logger.info("File extraction completed and event published.")

        else:
            logger.error("Unknown message type: '%s'. Full message: %s", msg_type, message_dict)

    except Exception as e:
        logger.error("Extraction failed: %s", e, exc_info=True)
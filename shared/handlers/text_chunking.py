from chunking import chunk_text

from config import CHUNK_OVERLAP, CHUNK_SIZE
from shared.pubsub.publisher import publish_event


def process_text_message(payload: dict, output_topic: str):
    try:
        document_id = payload["document_id"]
        tenant_id = payload["tenant_id"]
        text = payload["text"]
        chunk_size = payload.get("chunk_size", CHUNK_SIZE)
        chunk_overlap = payload.get("chunk_overlap", CHUNK_OVERLAP)

        chunks = chunk_text(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            tenant_id=tenant_id,
            document_id=document_id,
        )

        for chunk in chunks:
            publish_event(output_topic, chunk)

    except Exception as e:
        # In production, log or send to a DLQ
        print(f"Error processing message: {e}")

import logging
import signal
import sys

from extractor import handle_ingestion_event

from config import PUBSUB_TOPIC, SUBSCRIPTION_NAME
from shared.pubsub.subscriber import subscribe_to_topic

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Graceful shutdown handler


def shutdown_handler(signum, frame):
    logger.info("Shutdown signal received. Exiting gracefully...")
    sys.exit(0)


if __name__ == "__main__":
    # Register termination signals
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info("Starting extractor service...")
    logger.info(f"Subscribing to topic '{PUBSUB_TOPIC}' with subscription '{SUBSCRIPTION_NAME}'")

    # Begin subscription loop
    subscribe_to_topic(
        topic=PUBSUB_TOPIC,
        subscription=SUBSCRIPTION_NAME,
        callback=handle_ingestion_event,
        raw_message=False,
    )

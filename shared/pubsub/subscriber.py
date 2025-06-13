import json
import logging
import signal
import sys
import traceback
from typing import Callable, Union

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message

from config import GCP_PROJECT


def to_serializable(obj):
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        return to_serializable(vars(obj))
    elif hasattr(obj, "items"):
        try:
            return dict(obj.items())
        except Exception:
            return str(obj)
    else:
        try:
            json.dumps(obj)  
            return obj
        except Exception:
            return str(obj)

logger = logging.getLogger("pubsub_subscriber")
logging.basicConfig(
    level=logging.INFO,
    format=json.dumps(
        {
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s",
            "component": "subscriber",
            "message": "%(message)s",
        }
    ),
    handlers=[logging.StreamHandler(sys.stdout)],
)

if not GCP_PROJECT:
    raise ValueError("GCP_PROJECT environment variable is not set.")


# Main Subscriber Function
def subscribe_to_topic(
    topic: str,
    subscription: str,
    callback: Callable[[Union[dict, Message]], None],
    raw_message: bool = False,
):
    subscriber = pubsub_v1.SubscriberClient()
    sub_path = subscriber.subscription_path(GCP_PROJECT, subscription)

    def wrapped_callback(message: Message):
        try:
            raw_data = message.data.decode("utf-8", errors="replace")
            attributes = message.attributes or {}

            if not raw_data.strip():
                logger.warning(
                    json.dumps(
                        {"event": "EmptyMessageReceived", "attributes": to_serializable(attributes)}
                    )
                )
                message.ack()
                return

            try:
                payload = json.loads(raw_data)
                logger.info(
                    json.dumps(
                        {
                            "event": "MessageReceived",
                            "attributes": to_serializable(attributes),
                            "payload_preview": str(payload)[:200],
                        }
                    )
                )
                callback(payload)
                message.ack()
            except json.JSONDecodeError as je:
                logger.error(
                    json.dumps({"event": "JSONDecodeError", "error": str(je), "raw_data": raw_data})
                )
                message.ack()  # Don't retry bad data
        except Exception as e:
            logger.error(
                json.dumps(
                    {"event": "CallbackError", "error": str(e), "traceback": traceback.format_exc()}
                )
            )
            message.nack()  # Retry

    logger.info(json.dumps({"event": "SubscriberStarted", "subscription": sub_path}))
    streaming_pull_future = subscriber.subscribe(sub_path, callback=wrapped_callback)

    def shutdown_handler(signum, frame):
        logger.info(json.dumps({"event": "ShutdownSignalReceived"}))
        streaming_pull_future.cancel()
        try:
            streaming_pull_future.result(timeout=5)
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        streaming_pull_future.result()
    except Exception as e:
        logger.error(
            json.dumps(
                {"event": "StreamingError", "error": str(e), "traceback": traceback.format_exc()}
            )
        )

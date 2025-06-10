import json
import signal
import sys
import traceback
from typing import Callable, Union

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message

from config import GCP_PROJECT

if not GCP_PROJECT:
    raise ValueError("GCP_PROJECT environment variable is not set.")


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

            if raw_message:
                print("Received raw message")
                callback(message)
            else:
                if not raw_data.strip():
                    print("Warning: Received empty message body.")
                    message.ack()
                    return

                try:
                    payload = json.loads(raw_data)
                    print(f"Received message: {payload}")
                    callback(payload)
                except json.JSONDecodeError as je:
                    print(f"JSON decode error: {je} | Raw data: {repr(raw_data)}")
                    message.ack()
                    return

            message.ack()
        except Exception as e:
            print(f"Unhandled error processing message: {e}")
            traceback.print_exc()
            message.nack()

    print(f"Listening on {sub_path} ...")
    streaming_pull_future = subscriber.subscribe(sub_path, callback=wrapped_callback)

    def shutdown_handler(signum, frame):
        print("Shutdown signal received. Cancelling subscription...")
        streaming_pull_future.cancel()
        try:
            streaming_pull_future.result(timeout=5)
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        streaming_pull_future.result()  # Blocking call
    except Exception as e:
        print(f"Listening stopped due to error: {e}")
        traceback.print_exc()

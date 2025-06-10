from google.cloud import pubsub_v1

from config import GCP_PROJECT


# pubsub_client.py
class PubSubClient:
    def __init__(self, project_id: str, topic_id: str):
        self.project_id = project_id
        self.topic_id = topic_id
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project_id, topic_id)

    def publish_message(self, message_str: str, attributes: dict = None):
        data = message_str.encode("utf-8")  # Encode the message to bytes
        future = self.publisher.publish(self.topic_path, data, **(attributes or {}))
        print(f"Published message ID: {future.result()}")
        return future.result()


if __name__ == "__main__":
    import sys

    project = GCP_PROJECT
    topic = "ingestion-request"
    client = PubSubClient(project, topic)

    msg = "Test message"
    if len(sys.argv) > 1:
        msg = sys.argv[1]

    client.publish_message(msg)

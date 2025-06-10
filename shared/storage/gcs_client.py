from google.cloud import storage

from config import GCS_BUCKET


def download_file_from_gcs(gcs_path: str, local_path: str):

    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET)
    blob = bucket.blob(gcs_path)
    blob.download_to_filename(local_path)

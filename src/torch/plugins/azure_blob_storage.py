import os

from azure.storage.blob import BlobServiceClient, BlobClient


def upload_to_azure(container_name, blob_name):
    cloud_connection_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if cloud_connection_str:
        blob_service_client = BlobServiceClient.from_connection_string(cloud_connection_str)
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name)

        with open(file=destination, mode="rb") as data:
            blob_client.upload_blob(data)
            return blob_client.url
    else:
        return None

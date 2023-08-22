import os

from io import BytesIO
from azure.storage.blob import ContainerClient
from urllib.parse import urlparse


def upload(url: str, file_bytes: BytesIO):
    o = urlparse(url)
    host = o.netloc
    folder = os.path.dirname(o.path)
    bucket = os.path.dirname(o.path)
    while os.path.dirname(bucket) != '/':
        bucket = os.path.dirname(bucket)
    
    folder = folder.replace(bucket, '')
    bucket = bucket.replace('/', '')
    filename = f'{folder}/{os.path.basename(o.path)}'
    
    container = ContainerClient.from_connection_string(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"), bucket)
    if not container.exists():
        container.create_container(public_access="blob")
    
    container.upload_blob(filename, file_bytes.read(), overwrite=True)

    return f"https://{host}/{bucket}{folder}{filename}"
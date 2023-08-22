import os

from io import BytesIO
from minio import Minio
from urllib.parse import urlparse


def upload(url: str, username: str, password: str, file_bytes: BytesIO):
    if not url.startswith('s3'):
        url = f's3://{url}'
    
    o = urlparse(url)
    host = o.netloc
    folder = os.path.dirname(o.path)
    bucket = os.path.dirname(o.path)
    while os.path.dirname(bucket) != '/':
        bucket = os.path.dirname(bucket)
    
    folder = folder.replace(bucket, '')
    bucket = bucket.replace('/', '')
    filename = f'{folder}/{os.path.basename(o.path)}'
    
    client = Minio(host, access_key=username, secret_key=password)

    if not client.bucket_exists(bucket):
       client.make_bucket(bucket)

    image_size = file_bytes.getbuffer().nbytes
    
    client.put_object(bucket, filename, file_bytes, image_size, content_type='image/jpeg')

    return f"s3://{host}{folder}/{filename}"
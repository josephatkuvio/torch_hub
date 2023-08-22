import os
import boto3
import paramiko
import requests
from io import BytesIO

from botocore.config import Config
from botocore.exceptions import ClientError
from minio import Minio

from torch_tasks import torch_task
from torch_api.models import Specimen, Connection


@torch_task("Transfer")
def upload(specimen: Specimen, upload_folder: str, upload_type='sftp', host=None, username=None, password=None):
   # password = decrypt(password)
   try:
       result = {}
       for image in specimen.images:
           if upload_type == "sftp":
               image.external_url = upload_via_paramiko_sftp(upload_folder, image.url, host, username, password)
           elif upload_type == "minio":
               image.external_url = upload_via_minio(upload_folder, image.url, host, username, password)
           else:
               raise NotImplementedError(f"Upload type {upload_type} is not yet implemented.")
           result[image.size] = image.external_url

       return result
   except Exception as e:
       return f"An error occurred: {e}"
    


def upload_via_paramiko_sftp(collection_folder, path, host, username, password):
   transport = paramiko.Transport((host, 22))
   transport.connect(username=username, password=password)
   sftp = paramiko.SFTPClient.from_transport(transport)
   image_bytes = BytesIO(requests.get(path, stream=True).content)

   mkdir_p(sftp, collection_folder)
   sftp.putfo(image_bytes, os.path.basename(path))
   final_url = f"{host}" + sftp.getcwd() + f"/{os.path.basename(path)}"
   sftp.close()
   transport.close()

   return final_url


def upload_via_minio(collection_folder, path, host, username, password):
   client = Minio(
       host,
       access_key=username,
       secret_key=password,
   )

   found = client.bucket_exists(collection_folder)
   if not found:
       client.make_bucket(collection_folder)
   else:
       print(f"Bucket {collection_folder} already exists")

   r = requests.get(path, stream=True)
   image_bytes = BytesIO(r.content)
   image_size = image_bytes.getbuffer().nbytes
    
   client.put_object(collection_folder, os.path.basename(path), image_bytes, image_size, content_type='image/jpeg')
   hostnoport = host.split(":")[0]

   #files = client.list_objects(collection_folder, recursive=True)
   #for file in files:
   #    print(file)

   return f"https://{hostnoport}/{collection_folder}/{os.path.basename(path)}"


def mkdir_p(sftp, remote_directory):
   if remote_directory == "/":
       sftp.chdir("/")
       return
   if remote_directory == "":
       return
   try:
       sftp.chdir(remote_directory)  # subdirectory exists
   except IOError:
       dirname, basename = os.path.split(remote_directory.rstrip("/"))
       mkdir_p(sftp, dirname)  # make parent directories
       sftp.mkdir(basename)  # subdirectory missing, so created it
       sftp.chdir(basename)
       return True

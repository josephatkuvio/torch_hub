import os

from paramiko import SFTPClient, Transport
from io import BytesIO
from urllib.parse import urlparse


def mkdir_p(sftp: SFTPClient, dirname: str):
   if dirname == "/":
       sftp.chdir("/")
       return
   if dirname == "":
       return
   try:
       sftp.chdir(dirname)  # subdirectory exists
   except IOError:
       dirname, basename = os.path.split(dirname.rstrip("/"))
       mkdir_p(sftp, dirname)  # make parent directories
       sftp.mkdir(basename)  # subdirectory missing, so created it
       sftp.chdir(basename)
       return True


def upload(url: str, username: str, password: str, file_bytes: BytesIO):
    o = urlparse(url)
    host = o.netloc
    folder = os.path.dirname(o.path)
    filename = os.path.basename(o.path)
    
    transport = Transport(host, 22)
    transport.connect(username=username, password=password)
    
    sftp = SFTPClient.from_transport(transport)
    mkdir_p(sftp, folder)
    sftp.putfo(file_bytes, filename)

    sftp.close()
    transport.close()
    
    return f"sftp://{host}" + sftp.getcwd() + f"/{filename}"

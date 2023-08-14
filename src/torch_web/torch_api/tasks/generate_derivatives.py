import os
import traceback
import requests

from pathlib import Path
from typing import Optional

from PIL import Image
from io import BytesIO
from datetime import datetime
from torch_api.torch_tasks import torch_task
from torch_api.models import Specimen, SpecimenImage
from azure.storage.blob import BlobServiceClient


def parse_sizes(sizes):
    items = [item.strip() for item in sizes.split(",")]
    output_dict = {}

    # loop through the items
    for item in items:
      # split the item by colon and strip any whitespace
      key_value = [kv.strip() for kv in item.split(":")]
      # if there is only one element, it is the key and the value is None
      if len(key_value) == 1:
        output_dict[key_value[0]] = None
      # if there are two elements, they are the key and the value
      elif len(key_value) == 2:
        # try to convert the value to an integer
        try:
          value = int(key_value[1])
        # if it fails, use the original value as a string
        except ValueError:
          value = key_value[1]
        # add the key-value pair to the dictionary
        output_dict[key_value[0]] = value

    # print the output dictionary
    return output_dict


@torch_task("Generate Derivatives")
def generate_derivatives(specimen: Specimen, sizes_to_generate, hash_size=32):
    sizes = parse_sizes(sizes_to_generate)

    derivatives_to_add = {
        size: config
        for size, config in sizes.items()
        if not any(image.size == size for image in specimen.images)
    }

    result = {}
    original_image = specimen.download()
    
    for derivative in derivatives_to_add.keys():
        new_derivative = generate_derivative(specimen, original_image, derivative, derivatives_to_add[derivative])

        if new_derivative is not None:
            new_derivative.hash(hash_size)
            specimen.images.append(new_derivative)
                
            result[derivative] = {
                "url": new_derivative.output_file,
                "size": new_derivative.size,
                "width": new_derivative.width,
                "height": new_derivative.height
            }

    return result


def generate_derivative(specimen: Specimen, image: BytesIO, size: str, width: int) -> Optional[SpecimenImage]:
    full_image_path = Path(specimen.input_file)
    derivative_file_name = f"{full_image_path.stem}_{size}{full_image_path.suffix}"
    derivative_path = f"{specimen.batch_id}/_artifacts/{derivative_file_name}"

    img = Image.open(image)

    if width is not None:
        img.thumbnail((width, width))

    blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"))
    blob_client = blob_service_client.get_blob_client(container=f"workflow-{specimen.input_connection.workflow_id}-input", blob=derivative_path)
    image_stream = BytesIO()
    img.save(image_stream, format='JPEG')
    image_stream.seek(0)
    blob_client.upload_blob(image_stream.read(), overwrite=True)

    specimen_image = SpecimenImage(
        specimen_id=specimen.id,
        size=size,
        height=img.height,
        width=img.width,
        output_file=blob_client.url,
        create_date=datetime.now()
    )

    return specimen_image

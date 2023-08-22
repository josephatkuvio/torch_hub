from torch_api.torch_tasks import torch_task
from torch_api.models import Specimen

from PIL import Image


@torch_task("Check Portrait Orientation")
def check_orientation(specimen: Specimen):
    with Image.open(specimen.download()) as im:
        width, height = im.size
        if height < width:
            raise ValueError(f"Orientation of {specimen.input_file} is landscape (height: {height}, width: {width}")
        
        return {
            "Orientation": "Portrait",
            "Height": height,
            "Width": width
        }

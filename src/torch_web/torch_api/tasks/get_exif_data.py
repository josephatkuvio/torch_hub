from torch_api.torch_tasks import torch_task
from torch_api.models import Specimen

from PIL import Image, TiffImagePlugin
from PIL.ExifTags import TAGS


def cast(v):
    try:
        if isinstance(v, TiffImagePlugin.IFDRational):
            return float(v)
        elif isinstance(v, tuple):
            return tuple(cast(t) for t in v)
        elif isinstance(v, bytes):
            return v.decode(errors="replace")
        elif isinstance(v, dict):
            for kk, vv in v.items():
                v[kk] = cast(vv)
            return v
        else: return v
    except Exception:
        return None


@torch_task("Get EXIF Info")
def get_exif_data(specimen: Specimen):
    """
    Extract EXIF data from an image.
    Args:
        specimen (Specimen): Working specimen context.
    Returns:
        dict: A dictionary containing the extracted EXIF data.
    """

    # Open the image
    image = Image.open(specimen.download())

    # Extract EXIF data
    exif_data = image._getexif()

    # Create a dictionary to store the extracted data
    exif_info = {}
    if exif_data is not None:
        for k, v in exif_data.items():
            if k in TAGS:
                v = cast(v)
                if v is not None:
                    exif_info[TAGS[k]] = v

    return exif_info
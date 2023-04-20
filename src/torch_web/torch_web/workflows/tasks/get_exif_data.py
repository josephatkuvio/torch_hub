from torch_web.collections import collections
from torch_web.workflows.workflows import torch_task

from PIL import Image
from PIL.ExifTags import TAGS

@torch_task("Get EXIF Info")
def get_exif_data(specimen: collections.Specimen):
    """
    Extract EXIF data from an image.
    Args:
        image_path (str): Path to the image file.
    Returns:
        dict: A dictionary containing the extracted EXIF data.
    """
    print("Hello 1")
    # Open the image
    image = Image.open(specimen.upload_path)

    # Extract EXIF data
    exif_data = image._getexif()

    # Create a dictionary to store the extracted data
    exif_info = {}
    if exif_data is not None:
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            exif_info[tag_name] = value
    exif_info.get()
    # Accessing individual EXIF data
    print("Hello2")
    #print("Image Make: ", exif_info.get('Make'))
    #print("Image Model: ", exif_info.get('Model'))
    #print("Image Exposure Time: ", exif_info.get('ExposureTime'))
    #print("Image Focal Length: ", exif_info.get('FocalLength'))
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        print(f'Tag: {tag_name}, Value: {value}')
    # ... and so on
    return exif_info

## Example usage
#image_path = 'example.jpg'  # Replace with your own image file path
#exif_info = get_exif_data(image_path)


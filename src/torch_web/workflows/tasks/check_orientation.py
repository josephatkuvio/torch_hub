from torch_web.collections import specimens
from torch_web.workflows.workflows import torch_task


@torch_task("Check Portrait Orientation")
def check_orientation(specimen: specimens.Specimen, context):
    if not specimens.is_portrait(specimen.upload_path):
        return f"Specimen {specimen.id}-{specimen.name} incorrect orientation"

    return specimen

from sqlalchemy import or_, select
from sqlmodel import Session
from torch_api.torch_tasks import torch_task
from torch_api.models import Specimen, SpecimenImage
from torch_api.database import engine


@torch_task("Check for Duplicate Image")
def check_duplicate(specimen: Specimen, max_distance=35):
    """
    Compares all specimen image hashes against other hashes to 
    ensure uniqueness in the specimen database
    """
    result = {}
    
    with Session(engine) as session:
        for img in specimen.images:
            split_filter = or_(SpecimenImage.hash_a == img.hash_a,
                                SpecimenImage.hash_b == img.hash_b,
                                SpecimenImage.hash_c == img.hash_c,
                                SpecimenImage.hash_d == img.hash_d)

            similar_images = session.scalars(select(SpecimenImage).filter(SpecimenImage.id != img.id, SpecimenImage.hash_a is not None, split_filter))
            too_close_images = [sim for sim in similar_images if abs(sim.average_hash() - img.average_hash()) < int(max_distance)]

            if len(too_close_images) > 0:
                distance = abs(too_close_images[0].average_hash() - img.average_hash())
                raise ValueError(f"Specimen image {img.output_file} is too similar to {too_close_images[0].url}. Distance is {distance}")
            else:
                result[img.name] = f"No duplicates found within distance {distance}"

    return result

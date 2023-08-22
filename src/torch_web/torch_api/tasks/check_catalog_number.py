from ctypes import ArgumentError
import re
from torch_api.models import Specimen
from torch_api.torch_tasks import torch_task

@torch_task("Extract Catalog Number")
def check_catalog_number(specimen: Specimen, catalog_number_regex, catalog_group_name='catNum'):
    """
    Extracts the catalog number from the specimen's file name.
    
    :param str catalog_number_regex: 
    """

    if catalog_number_regex is not None:
        c = re.search(catalog_number_regex, specimen.name)
        if c is not None and c.group(catalog_group_name) is not None:
            specimen.catalog_number = c.group(catalog_group_name)
        else:
            raise ValueError(f'No catalog number could be extracted from {specimen.name}')    
    else:
        raise ArgumentError('No catalog number regex was provided.')


    return { 
        "Catalog Number": specimen.catalog_number
    }

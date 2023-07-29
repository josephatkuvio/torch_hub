import functools
import inspect
from typing import List

from .models import Task


torch_task_registry: List[Task] = []

    
def torch_task(name, description=None):
    def decorate(func):
        global torch_task_registry
        spec = inspect.signature(func)
        parameters = dict([(k, v.default if v.default is not inspect.Parameter.empty else None) for k, v in spec.parameters.items() if k != 'specimen'])
        torch_task_registry.append(Task(name=name, description=description, func_name=func.__name__, parameters=parameters))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        return wrapper
    return decorate
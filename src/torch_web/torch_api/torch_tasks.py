import functools
import inspect
import pickle
import os
from types import SimpleNamespace

from torch_api.models import CatalogTask

task_cache_file = 'tasks.pkl'


def torch_task(name, description=None):
    def decorate(func):
        spec = inspect.signature(func)
        parameters = dict([(k, v.default if v.default is not inspect.Parameter.empty else None) for k, v in spec.parameters.items() if k != 'specimen'])

        all_tasks = []
        if os.path.exists(task_cache_file):
            with open(task_cache_file, 'rb') as tasks:
                all_tasks = pickle.load(tasks)
        
        task = CatalogTask(name=name, description=description if description is not None else '', func_name=func.__name__, parameters=parameters)
        all_tasks = [t for t in all_tasks if t.func_name != task.func_name]
        all_tasks.append(task)
        with open(task_cache_file, 'wb') as tasks:
            pickle.dump(all_tasks, tasks)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        return wrapper
    return decorate


def get_all_tasks():
    with open(task_cache_file, 'rb') as infile:
        return pickle.load(infile)
from concurrent.futures import ThreadPoolExecutor
import importlib
import requests
import imagehash
import json

from io import BytesIO
from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, Session
from .database import engine

     
class Collection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: str
    deleted_date: Optional[datetime]
    specimens: List["Specimen"] = Relationship(back_populates="collection")


class Workflow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    collection_id: int = Field(foreign_key="collection.id")
    name: str
    description: Optional[str]
    create_date: datetime
    tasks: List["Task"] = Relationship(back_populates="workflow")

    def start_many(self, specimens: List["Specimen"], max_workers:int=10):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for specimen in specimens:
                executor.submit(self.start, specimen)

    def start(self, specimen: "Specimen"):
        with Session(engine) as session:
            session.merge(specimen)
            session.merge(self)

            for img in specimen.images:
                if img.size == 'FULL':
                    img.image_bytes = BytesIO(requests.get(img.url, stream=True).content)
        
            for task in self.tasks:
                specimen_task = SpecimenTask(specimen_id=specimen.id, task_id=task.id, start_date=datetime.datetime.now())
                specimen.tasks.append(specimen_task)
                session.commit()
                
                task.start(specimen)

            #context.socketio.emit('specimen_added', specimen_id);


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: Optional[int] = Field(default=None, foreign_key="workflow.id")
    func_name: str
    name: str
    sort_order: Optional[int]
    description: Optional[str]
    workflow: Workflow = Relationship(back_populates="tasks")
    parameters: List["Parameter"] = Relationship(back_populates="task")

    def start(self, specimen: "Specimen"):
        with Session(engine) as session:
            session.merge(self)

            self.run_state = 'Running'
            #context.socketio.emit('specimen_task_updated', specimen_task)
            
            module = importlib.import_module('tasks.' + self.func_name)
            func = getattr(module, self.func_name)
            result = func(specimen, **self.parameters_dict())
            session.commit()
            
            if isinstance(result, str):
                self.run_state = 'Error'
                self.error_message = result
            else:
                self.end_date = datetime.datetime.now()
                self.run_state = 'Success'
                self.run_message = json.dumps(result)
                session.commit()

            #context.socketio.emit('specimen_task_updated', specimen_task)


class Parameter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    name: str
    value: str
    task: Task = Relationship(back_populates="parameters")


class Specimen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    collection_id: int = Field(foreign_key="collection.id")
    workflow_id: Optional[int] = Field(foreign_key="workflow.id")
    name: str
    create_date: datetime
    upload_path: str
    barcode: Optional[str]
    catalog_number: Optional[str]
    batch_id: Optional[str]
    deleted: bool = Field(default=False)
    has_dng: bool = Field(default=False)
    images: List["SpecimenImage"] = Relationship(back_populates="specimen")
    tasks: List["SpecimenTask"] = Relationship(back_populates="specimen")
    collection: Collection = Relationship(back_populates="specimens")

    def image_bytes(self):
        for img in self.images:
            if img.size == 'FULL':
                return img.image_bytes
        
        return None


class SpecimenTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    specimen_id: int = Field(foreign_key="specimen.id")
    task_id: int = Field(foreign_key="task.id")
    start_date: datetime
    end_date: Optional[datetime]
    run_state: Optional[str]
    run_message: Optional[str]
    task: Task = Relationship(back_populates="specimen_tasks")
    specimen: Specimen = Relationship(back_populates="tasks")


class SpecimenImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    size: str
    height: Optional[int]
    width: Optional[int]
    url: Optional[str]
    create_date: datetime
    specimen_id: int = Field(foreign_key="specimen.id")
    specimen: Specimen = Relationship(back_populates="images")
    external_url: Optional[str]
    hash_a: Optional[str]
    hash_b: Optional[str]
    hash_c: Optional[str]
    hash_d: Optional[str]

    def average_hash(self):
        return imagehash.hex_to_hash(f'{self.hash_a}{self.hash_b}{self.hash_c}{self.hash_d}')


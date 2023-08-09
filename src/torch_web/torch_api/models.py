from concurrent.futures import ThreadPoolExecutor
import importlib
from PIL import Image
import requests
import imagehash
import json

from io import BytesIO
from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, Session, Column, JSON
from .database import engine

     
class Institution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: str
    created_date: datetime
    owner_id: int = Field(foreign_key="user.id")
    deleted_date: Optional[datetime]
    workflows: List["Workflow"] = Relationship(back_populates="institution")


class Workflow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    institution_id: int = Field(foreign_key="institution.id")
    name: str
    description: Optional[str]
    created_date: datetime
    deleted_date: Optional[datetime]
    institution: Institution = Relationship(back_populates="workflows")
    tasks: List["Task"] = Relationship(back_populates="workflow")
    users: List["WorkflowUser"] = Relationship(back_populates="workflow")
    connections: List["Connection"] = Relationship(back_populates="workflow")     

    def start_many(self, specimens: List["Specimen"], max_workers:int=10):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for specimen in specimens:
                executor.submit(self.start, specimen)

    def start(self, specimen: "Specimen"):
        with Session(engine) as session:
            session.merge(specimen)
            session.merge(self)

            for task in self.tasks:
                task_run = TaskRun(specimen=specimen, task=task, start_date=datetime.datetime.now())
                specimen.tasks.append(task_run)
                session.commit()
                
                task_run.start()

            #context.socketio.emit('specimen_added', specimen_id);


class CatalogTask(SQLModel):
    name: str
    func_name: str
    description: Optional[str] = Field(nullable=True)
    parameters: dict


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: Optional[int] = Field(default=None, foreign_key="workflow.id")
    name: str
    func_name: str
    sort_order: Optional[int]
    description: Optional[str]
    last_updated_date: Optional[datetime]
    workflow: Workflow = Relationship(back_populates="tasks")
    parameters: dict = Field(default={}, sa_column=Column(JSON))
    runs: List["TaskRun"] = Relationship(back_populates="task")


class Connection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: Optional[int] = Field(default=None, foreign_key="workflow.id")
    direction: str
    name: str
    description: Optional[str]
    container_type: str
    host: Optional[str] 
    user_id: Optional[str]
    password_key: Optional[str]
    application_id: Optional[str]
    application_key: Optional[str]
    workflow: Workflow = Relationship(back_populates="connections")
    specimen_count: Optional[int]
    specimens: List["Specimen"] = Relationship(back_populates="input_connection")


class Specimen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    input_connection_id: int = Field(foreign_key="connection.id")
    output_connection_id: Optional[int] = Field(foreign_key="connection.id", nullable=True)
    input_file: str
    name: str
    create_date: datetime
    batch_id: str
    processed_date: Optional[datetime]
    status: Optional[str]
    status_date: Optional[datetime]
    barcode: Optional[str]
    catalog_number: Optional[str]
    deleted: bool = Field(default=False)
    images: List["SpecimenImage"] = Relationship(back_populates="specimen")
    tasks: List["TaskRun"] = Relationship(back_populates="specimen")
    input_connection: Connection = Relationship(back_populates="specimens", foreign_key="Specimen.input_connection_id")
    
    def download(self):
        return BytesIO(requests.get(self.input_file, stream=True).content)



class TaskRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    specimen_id: int = Field(foreign_key="specimen.id")
    parameters: dict = Field(default={}, sa_column=Column(JSON))
    start_date: datetime
    end_date: Optional[datetime]
    status: Optional[str]
    result: Optional[str]
    task: Task = Relationship(back_populates="runs")
    specimen: Specimen = Relationship(back_populates="tasks")
    
    def start(self):
        with Session(engine) as session:
            session.merge(self)

            self.status = 'Running'
            session.commit()
            #context.socketio.emit('specimen_task_updated', specimen_task)
            
            module = importlib.import_module('tasks.' + self.task.func_name)
            func = getattr(module, self.task.func_name)
            
            try:
                result = func(self.specimen, **self.parameters)
                self.end_date = datetime.datetime.now()
                self.status = 'Success'
                self.result = json.dumps(result)
            except Exception as ex:
                self.status = 'Error'
                self.result = str(ex)

            session.commit()
            #context.socketio.emit('specimen_task_updated', specimen_task)


class SpecimenImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    output_file: str
    size: str
    height: Optional[int]
    width: Optional[int]
    create_date: datetime
    specimen_id: int = Field(foreign_key="specimen.id")
    specimen: Specimen = Relationship(back_populates="images")
    hash_a: Optional[str]
    hash_b: Optional[str]
    hash_c: Optional[str]
    hash_d: Optional[str]

    
    def download(self):
        return BytesIO(requests.get(self.output_file, stream=True).content)

    
    def average_hash(self):
        return imagehash.hex_to_hash(f'{self.hash_a}{self.hash_b}{self.hash_c}{self.hash_d}')
    

    def hash(self, hash_size, hashfunc="average"):
        with Image.open(self.download()) as im:
            size = int(hash_size)
            split_size = int(size/4)
            result = str(imagehash.average_hash(im, size) if hashfunc == "average" else imagehash.phash(im))
            split_hash = [result[i:i+split_size] for i in range(0, len(result), split_size)]
            self.hash_a = split_hash[0]
            self.hash_b = split_hash[1]
            self.hash_c = split_hash[2]
            self.hash_d = split_hash[3]


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    last_login_date: Optional[datetime]
    current_workflow_id: Optional[int] = Field(foreign_key="workflow.id")
    current_workflow: Optional["Workflow"] = Relationship()
    identities: List["Identity"] = Relationship(back_populates="user")
    workflows: List["WorkflowUser"] = Relationship(back_populates="user")


class Identity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    provider_name: str
    provider_id: str
    user: User = Relationship(back_populates="identities")


class WorkflowUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: int = Field(foreign_key="workflow.id")
    user_id: int = Field(foreign_key="user.id")
    created_date: datetime
    role: str
    workflow: Workflow = Relationship(back_populates="users")
    user: User = Relationship(back_populates="workflows")
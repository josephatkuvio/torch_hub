import asyncio
import importlib
import os
import requests
import imagehash
import json

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import Optional
from datetime import datetime
from urllib.parse import urlparse
from sqlmodel import Field, SQLModel, Relationship, Session, Column, JSON
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

from torch_api.database import engine
from torch_api.socket import sio as socketio
from torch_api.plugins import sftp, s3


def emit(specimen: "Specimen", workflow: "Workflow", event):
    data = { 
        'Status': specimen.status, 
        'StatusDate': specimen.status_date.isoformat(), 
        'SuccessCount': len([task for task in specimen.tasks if task.status == 'Success']),
        'ErrorCount': len([task for task in specimen.tasks if task.status == 'Error']),
        'TotalTaskCount': len(workflow.tasks)
    }
    
    asyncio.run(socketio.emit(event, data, [specimen.batch_id, f'workflow-{specimen.input_connection.workflow_id}']))
    asyncio.run(socketio.emit(f'{event}_{specimen.id}', data, [specimen.batch_id, f'workflow-{specimen.input_connection.workflow_id}']))

     
class Institution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: str
    created_date: datetime
    owner_id: int = Field(foreign_key="user.id")
    deleted_date: Optional[datetime]
    workflows: list["Workflow"] = Relationship(back_populates="institution")


class Workflow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    institution_id: int = Field(foreign_key="institution.id")
    name: str
    description: Optional[str]
    created_date: datetime
    deleted_date: Optional[datetime]
    institution: Institution = Relationship(back_populates="workflows")
    tasks: list["Task"] = Relationship(back_populates="workflow")
    users: list["WorkflowUser"] = Relationship(back_populates="workflow")
    connections: list["Connection"] = Relationship(back_populates="workflow")

    def start_many(self, specimens: list["Specimen"], max_workers: int=10):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for specimen in specimens:
                executor.submit(self.start, specimen)

    def start(self, specimen: "Specimen"):
        with Session(engine) as session:
            local_specimen = session.merge(specimen)
            workflow = session.merge(self)

            local_specimen.set_status('Starting...');
            session.commit()
            
            sorted_tasks = sorted(workflow.tasks, key=lambda x: x.sort_order)
            for task in sorted_tasks:
                task_run = TaskRun(specimen=local_specimen, task=task, start_date=datetime.now(), parameters=task.parameters)
                local_specimen.tasks.append(task_run)
                local_specimen.set_status(f'Running {task_run.task.name}...');
                session.commit()
                emit(local_specimen, workflow, 'task_started');

                task_run_status = task_run.start()
                session.refresh(local_specimen)
                emit(local_specimen, workflow, 'task_completed');
            
                if task_run_status.startswith("Error"):
                    local_specimen.set_status(task_run_status);
                    break
                    
            if not local_specimen.status.startswith("Error"):
                local_specimen.set_status('Processed');
                local_specimen.processed_date = datetime.now()
            
            session.commit()
            emit(local_specimen, workflow, 'specimen_processed');


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
    runs: list["TaskRun"] = Relationship(back_populates="task")


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
    specimens: list["Specimen"] = Relationship(
        back_populates="input_connection", 
        sa_relationship_kwargs={
            "primaryjoin": "Connection.id==Specimen.input_connection_id",
            "lazy": "joined"
        })
    
    def get_password(self):
        client = SecretClient(vault_url=os.environ.get('AZURE_KEY_VAULT_URI'), credential=DefaultAzureCredential())
        return client.get_secret(self.password_key)
        
    
    def upload(self, image: "SpecimenImage"):
        if (self.direction != 'Output'):
            raise Exception("Cannot upload to an input connection")

        image_bytes = image.download()
        password = self.get_password()
        o = urlparse(self.host)
        url = f'{o.netloc}{os.path.dirname(o.path)}/{os.path.basename(image.url)}'

        if self.container_type == "sftp":
            image.output_file = sftp.upload(url, self.user_id, password, image_bytes)

        elif self.container_type == "s3":
            image.output_file = s3.upload(url, self.user_id, password, image_bytes)
        
        else:
            raise NotImplementedError(f"Upload type {self.container_type} is not yet implemented.")


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
    images: list["SpecimenImage"] = Relationship(back_populates="specimen")
    tasks: list["TaskRun"] = Relationship(back_populates="specimen")
    input_connection: Connection = Relationship(
        back_populates="specimens", 
        sa_relationship_kwargs=dict(foreign_keys="[Specimen.input_connection_id]"))
    
    def download(self):
        return BytesIO(requests.get(self.input_file, stream=True).content)
    
    def set_status(self, status: str):
        self.status = status
        self.status_date = datetime.now()



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
            task_run = session.merge(self)

            task_run.status = 'Running'
            task_run.start_date = datetime.now()
            session.commit()
            
            module = importlib.import_module('torch_api.tasks.' + task_run.task.func_name)
            func = getattr(module, task_run.task.func_name)
            
            try:
                result = func(task_run.specimen, **task_run.parameters)
                task_run.end_date = datetime.now()
                task_run.status = 'Success'
                task_run.result = json.dumps(result)
            except Exception as ex:
                task_run.status = 'Error: ' + task_run.task.name
                task_run.result = str(ex)

            session.commit()
            return task_run.status


class SpecimenImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    output_file: str
    size: str
    height: Optional[int]
    width: Optional[int]
    create_date: datetime
    specimen_id: int = Field(foreign_key="specimen.id")
    specimen: Specimen = Relationship(back_populates="images")
    url: Optional[str]
    hash_a: Optional[str]
    hash_b: Optional[str]
    hash_c: Optional[str]
    hash_d: Optional[str]

    
    def download(self):
        return BytesIO(requests.get(self.url, stream=True).content)

    
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
    identities: list["Identity"] = Relationship(back_populates="user")
    workflows: list["WorkflowUser"] = Relationship(back_populates="user")


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
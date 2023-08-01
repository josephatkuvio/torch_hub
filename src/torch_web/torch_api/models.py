from concurrent.futures import ThreadPoolExecutor
import importlib
import requests
import imagehash
import json

from io import BytesIO
from typing import Dict, List, Optional
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

            input_file = BytesIO(requests.get(specimen.input_file, stream=True).content)
        
            for task in self.tasks:
                specimen_task = SpecimenTask(specimen_id=specimen.id, task_id=task.id, start_date=datetime.datetime.now())
                specimen.tasks.append(specimen_task)
                session.commit()
                
                task.start(specimen)

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


class Specimen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    input_connection_id: int = Field(foreign_key="connection.id")
    output_connection_id: Optional[int] = Field(foreign_key="connection.id")
    input_file: str
    name: str
    create_date: datetime
    barcode: Optional[str]
    catalog_number: Optional[str]
    deleted: bool = Field(default=False)
    images: List["SpecimenImage"] = Relationship(back_populates="specimen")
    tasks: List["TaskRun"] = Relationship(back_populates="specimen")


class TaskRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    specimen_id: int = Field(foreign_key="specimen.id")
    parameters: Dict = Field(default={}, sa_column=Column(JSON))
    start_date: datetime
    end_date: Optional[datetime]
    status: Optional[str]
    result: Optional[str]
    task: Task = Relationship(back_populates="runs")
    specimen: Specimen = Relationship(back_populates="tasks")


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

    def average_hash(self):
        return imagehash.hex_to_hash(f'{self.hash_a}{self.hash_b}{self.hash_c}{self.hash_d}')


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
import uvicorn

from typing import List
from sqlmodel import Session, select
from fastapi import FastAPI, BackgroundTasks
from fastapi_socketio import SocketManager

from torch_api.database import create_db_and_tables, engine
from torch_api.models import Specimen, Workflow
from torch_api.torch_tasks import torch_task_registry


app = FastAPI()
socket_manager = SocketManager(app=app)


@app.get("/")
def root():
    return "TORCH Engine is running."


@app.get("/tasks", operation_id="GetAllTasks")
def tasks_getall():
    return { 'tasks': torch_task_registry }


@app.post("/workflows/{workflow_id}/{batch_id}", operation_id="StartWorkflow")
def workflows_start(workflow_id: int, batch_id: str, background_tasks: BackgroundTasks):
    with Session(engine) as session:
        query = select(Specimen).where(Specimen.batch_id == batch_id)
        specimens = session.exec(query).all()
        workflow = session.get(Workflow, workflow_id)
        background_tasks.add_task(workflow.start_many, specimens)


@app.put('/collections/{collection_id}', operation_id="UpdateExternalUrl")
def specimens_update_external_url(collection_id:int, specimens: List[Specimen]):
    updated_specimens = []
    
    with Session(engine) as session:
        for specimen in specimens:
            query = select(Specimen).where(Specimen.collection_id == collection_id and Specimen.catalog_number == specimen.catalog_number)
            existing = session.exec(query).one_or_none()
            if existing:
                existing.external_url = specimen.external_url
                updated_specimens.append(existing)

        session.commit()

    return updated_specimens


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
    uvicorn.run('app:app', port=8000, log_level="info")


    

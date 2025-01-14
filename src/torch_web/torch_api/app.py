import uvicorn
import os

from sqlmodel import Session, select
from fastapi import FastAPI, BackgroundTasks, HTTPException

from torch_api.database import create_db_and_tables, engine
from torch_api.models import CatalogTask, Specimen, Workflow
from torch_api.torch_tasks import get_all_tasks
from torch_api.socket import init, sio

app = FastAPI()
init(app)


@app.get("/")
def root():
    return "TORCH Engine is running."


@app.get("/tasks", operation_id="GetAllTasks")
async def tasks_getall() -> list[CatalogTask]:
    try:
        for module in os.listdir(os.path.dirname(__file__) + '/tasks'):
            if module == '__init__.py' or module[-3:] != '.py':
                continue
            __import__('torch_api.tasks.' + module[:-3], locals(), globals())
        del module

        tasks = get_all_tasks()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflows/{workflow_id}/{batch_id}", operation_id="StartWorkflow")
def workflows_start(workflow_id: int, batch_id: str, background_tasks: BackgroundTasks):
    with Session(engine) as session:
        query = select(Specimen).where(Specimen.batch_id == batch_id)
        specimens = session.exec(query).all()
        workflow = session.get(Workflow, workflow_id)
        background_tasks.add_task(workflow.start_many, specimens)
    
    return { "status": "started" }


@app.put('/collections/{collection_id}', operation_id="UpdateExternalUrl")
def specimens_update_external_url(collection_id:int, specimens: list[Specimen]):
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


@sio.event
def monitor_batch(sid, batch_id):
    print(f'{sid} monitoring batch {batch_id}')
    sio.enter_room(sid, batch_id)


@sio.event
def leave_batch(sid, batch_id):
    print(f'{sid} leaving batch {batch_id}')
    sio.leave_room(sid, batch_id)


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
    uvicorn.run('app:app', port=8000, log_level="info")


    

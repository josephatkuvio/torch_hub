from torch import db, socketio
from torch.prefect_flows.process_specimen import process_specimen
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from torch.collections.specimens import Specimen, SpecimenImage
import os

def run_workflow(collection,file:FileStorage,target_dir,config):

    specimen, execute_workflow = upsert_specimen(collection, file, target_dir)

    if execute_workflow:
        notify_specimen_update(specimen,"Running")

        match collection.workflow:
            case 'process_specimen':
                state = process_specimen(collection, specimen,config, return_state=True)
            case _:
                raise NotImplementedError 
        
        notify_specimen_update(specimen,state.name)

def upsert_specimen(collection, file, target_dir):
    sfilename = secure_filename(file.filename)
    filename = sfilename.split('.')[0]
    extension = sfilename.split('.')[1]
    execute_workflow = True

    specimen = db.session.query(Specimen).filter(Specimen.name == filename).first()

    destination = os.path.join(target_dir, sfilename)

    if os.path.exists(destination):
        return specimen, False

    file.save(destination)
        
    if specimen != None:
        if extension.lower() == 'dng':
            specimen.has_dng = 1
            execute_workflow = False
            
        else:
            execute_workflow = (specimen.flow_run_id != None)
        
    else:
        specimen = Specimen(name=filename, upload_path=destination, collection_id=collection.id)
        db.session.add(specimen)
        db.session.commit()
    
    upsert_specimen_image(specimen, destination, extension.lower())
    
    return specimen, execute_workflow
        
    
def upsert_specimen_image(specimen, destination, extension):
    size = "FULL"
    if extension == "dng":
        size = "DNG"
    
    si = db.session.query(SpecimenImage).filter(SpecimenImage.specimen_id == specimen.id).filter(SpecimenImage.size == size).first()
    
    if si == None:
        new_si = SpecimenImage(specimen_id=specimen.id,url=destination,size=size)
        db.session.add(new_si)
        db.session.commit()

def notify_specimen_update(specimen,state):
    db.session.refresh(specimen)
    socketio.emit('notify',{"id":specimen.id, "name": specimen.name, "cardimg": specimen.card_image(), "create_date": str(specimen.create_date), "flow_run_state":state, "failed_task": specimen.failed_task})

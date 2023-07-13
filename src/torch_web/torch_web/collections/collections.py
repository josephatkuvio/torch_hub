import datetime
import importlib
import os
import requests
import json

from operator import or_
from sqlalchemy import func, exists, select
from sqlalchemy.orm import joinedload, Session
from torch_web import db, executor
from prefect import context
from flask import current_app
from io import BytesIO
from torch_web.model import Collection, Specimen, SpecimenImage, CollectionTask, CollectionTaskParameter, SpecimenTask, SpecimenTaskParameter, CollectionUser, User


def get_collections(institutionid):
    collections_result = db.session.scalars(select(Collection).filter_by(institution_id=institutionid)).all()

    collections_dict = []
    for c in collections_result:
        cd = c.as_dict()
        cd["cardimg"] = get_collection_card_images(c.id)
        cd["specimencount"] = db.session.query(Specimen).filter(Specimen.collection_id == c.id).count()
        collections_dict.append(cd)

    return collections_dict


def get_collection_card_images(collection_id):
    img = db.session.scalars(select(SpecimenImage).join(Specimen)
                             .where(Specimen.collection_id == collection_id)
                             .where(Specimen.deleted == 0)
                             .where(SpecimenImage.size == 'THUMB').limit(10)).all()
    return img


def create_collection(institutionid, name, code):
    new_collection = Collection(
        name=name,
        code=code,
        institution_id=institutionid
    )

    local_collection = db.session.merge(new_collection)
    db.session.add(local_collection)
    db.session.commit()

    return local_collection


def update_workflow(collection_id, data):
    collection = db.session.get(Collection, collection_id)
    for task in collection.tasks:
        for p in task.parameters:
            db.session.delete(p)
        db.session.delete(task)
    db.session.commit()

    collection.tasks = []
    for task in data:
        new_task = CollectionTask()
        new_task.sort_order = task["sort_order"]
        new_task.func_name = task["func_name"]
        new_task.name = task["name"]
        collection.tasks.append(new_task)
        
        for p in task["parameters"]:
            new_p = CollectionTaskParameter()
            new_p.name = p["name"]
            new_p.value = p["value"]
            new_task.parameters.append(new_p)

    db.session.commit()


def get_collection(id):
    coll = db.session.scalars(select(Collection).where(Collection.id == id)).one_or_none()
    return coll


def get_collection_by_code(code):
    collec = db.session.scalars(select(Collection).where(Collection.code == code)).one_or_none()
    return collec


def get_collection_specimens(collectionid, search_string, only_error, page=1, per_page=14):
    specimens = select(Specimen).where(Specimen.collection_id == collectionid).where(Specimen.deleted == 0)

    if search_string is not None:
        specimens = specimens.filter(or_(Specimen.name.contains(search_string),
                                         Specimen.barcode.contains(search_string)))  # todo filter by status (?)

    if only_error == 'true':
        specimens = specimens.filter(func.lower(Specimen.flow_run_state) == 'failed')

    specimens = specimens.order_by(Specimen.id.desc()).limit(per_page).offset((page - 1) * per_page)
    result = db.session.scalars(specimens).all()

    specimensdict = []
    for s in result:
        sd = s.as_dict()
        sd["card_image"] = s.card_image()
        specimensdict.append(sd)

    return specimensdict


def retry_workflow(specimenid):
    specimen = db.session.get(Specimen, specimenid)
    collection = db.session.get(Collection, specimen.collection_id)
    run_workflow(collection.id, specimen.id)
    return True


def upload(collectionid, files):
    collection = db.session.get(Collection, collectionid)

    for file in files:
        specimen, execute_workflow = upsert_specimen(collection, file)
        context.socketio.emit('specimen_added', specimen.id);
        executor.submit(run_workflow, collection.id, specimen.id)
    
    return True


def get_specimen(specimenid):
    specimen = db.session.scalars(select(Specimen).options(joinedload(Specimen.tasks)).where(Specimen.id == specimenid)).first()
    return specimen


def get_specimen_by_catalog_number(collectionid, catalog_number):
    return db.session.scalars(select(Specimen).options(joinedload(Specimen.images)).where(
        Specimen.collection_id == collectionid,
        Specimen.catalog_number == catalog_number
    )).first()


def delete_collection(collection_id):
    collection = db.session.get(Collection, collection_id)

    if collection:
        specimens = db.session.scalars(select(Specimen).filter(Specimen.collection_id == collection_id)).all()
        print(specimens)

        collection.deleted_date = datetime.datetime.now()
        db.session.commit()

    return True


def delete_specimen(specimen_id):
    specimen = db.session.scalars(select(Specimen)
                                  .options(joinedload(Specimen.images))
                                  .where(Specimen.id == specimen_id)).first()
    
    print(specimen, specimen_id)
    if specimen:
        specimen.deleted = 1
        db.session.commit()

    return True


def delete_transfered_specimens(collectionid):
    collection = db.session.get(Collection, collectionid)

    if collection:
        specimens_has_non_transferred_images = exists(
            select([SpecimenImage.id])
            .select_from(SpecimenImage)
            .where((SpecimenImage.specimen_id == Specimen.id) &
                   (SpecimenImage.external_url is None))
        )

        specimens_with_transferred_images = (select([Specimen.id])
                                             .select_from(Specimen)
                                             .where((Specimen.collection_id == collectionid) &
                                                    (Specimen.deleted == 0) &
                                                    ~specimens_has_non_transferred_images)
                                             )

        specimens_ids = list(map(lambda x: x.id, db.session.scalars(specimens_with_transferred_images)))

        specimens = db.session.scalars(select(Specimen).options(joinedload(Specimen.images)).filter(Specimen.id.in_(specimens_ids))).all()

        for s in specimens:
            for i in s.images:
                delete_img_file(i.url)

            delete_img_file(s.upload_path)
            s.deleted = 1
            db.session.commit()

    return True


def delete_img_file(upload_path):
    if os.path.exists(upload_path):
        os.remove(upload_path)
    else:
        print("The file does not exist")


def export_csv(collectionid):
    collection = db.session.get(Collection, collectionid)

    if collection:
        specimens = db.session.scalars(select(Specimen).options(joinedload(Specimen.images))
                                       .filter(Specimen.collection_id == collectionid)
                                       .filter(Specimen.deleted == 0)
                                       .order_by(Specimen.id.desc())).all()

        si = io.StringIO()
        fieldnames = ['catalog_number', 'large', 'web', 'thumbnail']
        writer = csv.DictWriter(si, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()

        for s in specimens:
            large = get_specimen_img_url(s.images, 'FULL')
            web = get_specimen_img_url(s.images, 'MED')
            thumbnail = get_specimen_img_url(s.images, 'THUMB')
            if s.catalog_number is None:
                s.catalog_number = s.name
            writer.writerow({'catalog_number': s.catalog_number, 'large': large, 'web': web, 'thumbnail': thumbnail})

        return si.getvalue()


def get_specimen_img_url(specimen_images, size):
    list_imgs = list(filter(lambda x: x.size == size, specimen_images))
    if len(list_imgs) > 0:
        return list_imgs[0].external_url
    return None


def notify(session, task, specimen, state, message=None):
    task.run_state = state
    task.run_message = message
    session.commit()
    context.socketio.emit(task.func_name, (specimen.id, task.func_name, task.run_state, task.run_message))
    context.socketio.emit('specimen_updated_' + str(specimen.id), (specimen.catalog_number, task.func_name + ': ' + task.run_state))
     

def run_workflow(collection_id, specimen_id):

    with Session(db.engine) as session:
        collection = session.scalars(select(Collection).where(Collection.id == collection_id)).one_or_none()
        specimen = session.scalars(select(Specimen).options(joinedload(Specimen.tasks)).where(Specimen.id == specimen_id)).first()
    
        # Preload full image into memory
        for img in specimen.images:
            if img.size == 'FULL':
                img.image_bytes = BytesIO(requests.get(img.url, stream=True).content)
        
        for task in collection.tasks:
            specimen_task_parameters = [SpecimenTaskParameter(name=p.name, value=p.value) for p in task.parameters]
            specimen_task = SpecimenTask(func_name=task.func_name, name=task.name, description=task.description, sort_order=task.sort_order, parameters=specimen_task_parameters)
            specimen.tasks.append(specimen_task)

            notify(session, specimen_task, specimen, 'Running')
            
            module = importlib.import_module('torch_web.workflows.tasks.' + task.func_name)
            func = getattr(module, task.func_name)
            result = func(specimen, **task.parameters_dict())
            
            specimen_task.end_date = datetime.datetime.now()
            if isinstance(result, str):
                notify(session, specimen_task, specimen, 'Error', result)
                break
            
            notify(session, specimen_task, specimen, 'Success', json.dumps(result))

        context.socketio.emit('specimen_added', specimen_id);


def upsert_specimen(collection, file):
    filename = os.path.basename(file).split(".")[0]
    extension = os.path.basename(file).split(".")[1]

    execute_workflow = True

    specimen = Specimen(
        name=filename, upload_path=file, collection_id=collection.id
    )
    db.session.add(specimen)
    db.session.commit()

    upsert_specimen_image(specimen, file, extension.lower())

    return specimen, execute_workflow


def upsert_specimen_image(specimen, destination, extension):
    size = "FULL"
    if extension == "dng":
        size = "DNG"


    web_url = destination.replace(current_app.config['BASE_DIR'] + "\\", '').replace("\\", "/")
    si = next((img for img in specimen.images if img.size == size), None)

    if si is None:
        new_si = SpecimenImage(specimen_id=specimen.id, url=destination, external_url=web_url, size=size)
        specimen.images.append(new_si)
    else:
        si.url = web_url
    
    db.session.commit()


def get_collection_users(collection_id):
    collection_users = db.session.scalars(select(CollectionUser).join(User).filter(CollectionUser.collection_id == collection_id)).all()
  
    return collection_users


def add_user_to_collection(collection_id, user_id, role):
    add_collection_user = CollectionUser(collection_id=collection_id, user_id=user_id, role=role)

    db.session.add(add_collection_user)
    db.session.commit()

    return add_collection_user


def remove_user_from_collection(collection_id, user_id):
    remove_collection_user = db.session.scalars(select(CollectionUser)
                                         .filter(CollectionUser.collection_id == collection_id, CollectionUser.user_id == user_id)).one_or_none()
    
    if remove_collection_user:
        #db.session.delete(remove_collection_user)                 option to delete data in database

        #the following option just changes the value of collection_id to NULL
        remove_collection_user.collection_id = None                
        db.session.commit()

        return True

    return False


def update_user_role(collection_id, user_id, role):
    collection_user_role = db.session.scalars(select(CollectionUser)
                                         .filter(CollectionUser.collection_id == collection_id, CollectionUser.user_id == user_id)).one_or_none()
    
    if collection_user_role:
        collection_user_role.role = role
        db.session.commit()

        return collection_user_role

    return None
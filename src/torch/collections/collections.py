import json
from operator import or_
import os
from uuid import uuid4
from flask import Blueprint, flash, redirect, render_template, request, current_app, jsonify
from flask_security import current_user, login_required
from sqlalchemy import Column, Integer, String, ForeignKey, func, desc
from torch import db, Base
from torch.collections.specimens import Specimen, SpecimenImage
from torch.collections.workflow import run_workflow
from torch.institutions.institutions import Institution
from werkzeug.utils import secure_filename


class Collection(Base):
    __tablename__ = "collection"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    code = Column(String(10), unique=True)
    catalog_number_regex = Column(String(150))
    web_base = Column(String(150))
    url_base = Column(String(150))
    default_prefix = Column(String(15))
    barcode_prefix = Column(String(15))
    institution_id = Column(Integer, ForeignKey("institution.id"))
    flow_id = Column(String(150))
    workflow = Column(String(150))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def add_specimens(self, files, config) -> Specimen:
        batch_id = str(uuid4())
        target_dir = os.path.join(config['BASE_DIR'],"static","uploads", self.name, batch_id)
        os.makedirs(target_dir)
        
        for file in files:
            filename = secure_filename(file.filename)
            destination = os.path.join(target_dir, filename)
                        
            file.save(destination)

            specimen = Specimen(
                name=file.filename, upload_path=destination, collection_id=self.id
            )

            db.session.add(specimen)
            db.session.commit()
            
            run_workflow(self,specimen,config)
            
        

home_bp = Blueprint("home", __name__)
collections_bp = Blueprint("collections", __name__, url_prefix="/collections")


def get_default_institution():
    return db.session.query(Institution).first()


@home_bp.route("/", methods=["GET"])
def home():
    print("home collections")
    return redirect("/collections")

@collections_bp.route("/settings")
def collections_settings():
    return render_template("/collections/settings.html",user=current_user)

@collections_bp.route("/", methods=["GET"])
def collections():
    institution = get_default_institution()
    
    return render_template(
        "/collections/all_collections.html",
        user=current_user,
        institution=institution
    )


@collections_bp.route("/search", methods=["GET"])
def collections_search():
    institution = get_default_institution()
    
    collections = (
        db.session.query(Collection).filter_by(institution_id=institution.id).all()
    )

    collectionsdict = []
    for c in collections:
        cd = c.as_dict()
        cd["cardimg"] = getCollectionCardImage(c)
        collectionsdict.append(cd)
    
    return json.dumps(collectionsdict,indent=4, sort_keys=True, default=str)


def getCollectionCardImage(collection):
    img = db.session.query(SpecimenImage).join(Specimen).filter(Specimen.collection_id == collection.id).filter(SpecimenImage.size == 'THUMB').first()
    return img.web_url() if img != None else "../static/images/default.jpg"


@collections_bp.route("/", methods=["POST"])
def collectionspost():
    institution = get_default_institution()
    
    jcollection = request.get_json()
    newname = jcollection['name']

    if len(newname) < 1:
        flash("Name is too short!", category="error")
    else:
        new_collection = Collection(
            id = jcollection.get('id',None),
            name=newname,
            code=jcollection.get('code',None),
            institution_id=institution.id,
            flow_id = jcollection.get('flow_id',None),
            catalog_number_regex = jcollection.get('catalog_number_regex',None),
            default_prefix = jcollection.get('default_prefix',None),
            barcode_prefix = jcollection.get('barcode_prefix',None),
            workflow = 'process_specimen' #todo select with workflow options
        )
        
        local_collection = db.session.merge(new_collection)
        db.session.add(local_collection)
        db.session.commit()

    return jsonify({"collectionid": new_collection.id})


@collections_bp.route("/<collectioncode>", methods=["GET"])
def collection(collectioncode):
    collection = db.session.query(Collection).filter(func.lower(Collection.code) == func.lower(collectioncode)).first()
    return render_template("/collections/specimens.html", collection=collection)

@collections_bp.route("/specimens/<collectionid>", methods=["GET"])
def collection_specimens(collectionid):
    searchString = request.args.get('search_string')
    onlyError = request.args.get('only_error')
    collection = db.session.query(Collection).get(collectionid)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 14, type=int)

    specimens = db.session.query(Specimen).filter(Specimen.collection_id == collectionid).filter(Specimen.deleted == 0)

    if searchString != None : 
        specimens = specimens.filter(or_(Specimen.name.contains(searchString), Specimen.barcode.contains(searchString))) #todo filter by status (?)
    
    if onlyError == 'true' :
        specimens = specimens.filter(func.lower(Specimen.flow_run_state) == 'failed')

    totalSpecimens = specimens.count()

    specimens = specimens.order_by(Specimen.id.desc()).paginate(page, per_page=per_page)

    specimensdict = []
    for s in specimens.items:
        sd = s.as_dict()
        sd["cardimg"] = s.card_image()
        specimensdict.append(sd)

    return {'specimens': json.dumps(specimensdict,indent=4, sort_keys=True, default=str), 'totalSpecimens': totalSpecimens, 'collection': json.dumps(collection.as_dict(),indent=4, sort_keys=True, default=str)}

@collections_bp.route("/specimen/retry/<specimenid>", methods=["POST"])
def retry(specimenid):
    specimen = db.session.query(Specimen).get(specimenid)
    collection = db.session.query(Collection).get(specimen.collection_id)
    run_workflow(collection,specimen,config=current_app.config)
    return ajax_response(True,specimenid)


@collections_bp.route("/<collectionid>", methods=["POST"])
def upload(collectionid):
    collection = db.session.query(Collection).filter_by(code=collectionid).first()
    files = request.files.getlist("file")
    batch_id = collection.add_specimens(files, current_app.config)

    return ajax_response(True, batch_id)


@collections_bp.route("/<collectionid>/settings", methods=["GET", "POST"])
def settings(collectionid="default"):
    return render_template("/collections/settings.html", user=current_user)


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(
        dict(
            status=status_code,
            msg=msg,
        )
    )

@collections_bp.route("/<collectioncode>/<specimenid>", methods=["GET"])
def specimen(collectioncode, specimenid):
    collection = db.session.query(Collection).filter(func.lower(Collection.code) == func.lower(collectioncode)).first()
    specimen = db.session.query(Specimen).filter(Specimen.id == specimenid).first()
    images = db.session.query(SpecimenImage).filter(SpecimenImage.specimen_id == specimenid).all()
    
    orion_url = current_app.config["PREFECT_ORION_URL"] if current_app.config["PREFECT_ORION_URL"] != None else "http://127.0.0.1:4200/"
    prefect_url = orion_url  + "flow-run/" + specimen.flow_run_id
   
    return render_template("/collections/specimen.html", collection=collection, specimen=specimen, images=images, prefect_url = prefect_url)


@collections_bp.route("/<id>", methods=["DELETE"])
def delete(id):
    collection = db.session.query(Collection).get(id)

    if collection:
        specimens = db.session.query(Specimen).filter(Specimen.collection_id == id).all()
        print(specimens)
        if len(specimens) > 0:
            return jsonify({"status":"error","statusText":"Impossible to delete a collection with specimens."})
        
        db.session.delete(collection)
        db.session.commit()

    return jsonify({"status":"ok"})

@collections_bp.route("specimen/<id>", methods=["DELETE"])
def delete_specimen(id):
    specimen = db.session.query(Specimen).get(id)

    if specimen:        
        specimen.deleted = 1
        db.session.commit()

    return jsonify({"status":"ok"})
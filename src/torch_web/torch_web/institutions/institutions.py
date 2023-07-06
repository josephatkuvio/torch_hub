import datetime
from flask import flash
from sqlalchemy import select
from torch_web import db
from torch_web.model import Institution


def get_institutions():
    return db.session.scalars(select(Institution)).all()

def get_institution(id):
    inst = db.session.scalars(select(Institution).where(Institution.id == id)).one_or_none()
    return inst


def create_institution(name, code, admin_user):
    if len(name) < 1:
        flash("Name is too short!", category="error")
        return None

    new_institution = Institution(name=name, code=code)
    new_institution.users.append(admin_user)
    db.session.add(new_institution)
    db.session.commit()
    return new_institution


def delete_institution(institution_id):
    institution = db.session.get(Institution, institution_id)

    if institution:
        institution.deleted_date = datetime.datetime.now()
        db.session.commit()

    return True

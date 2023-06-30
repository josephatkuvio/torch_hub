import datetime
from flask import flash
from typing import List
from sqlalchemy import func, Integer, String, DateTime, select
from sqlalchemy.orm import Mapped, relationship, mapped_column
from torch_web import Base, db
from torch_web.users import User

     

class Institution(Base):
    __tablename__ = "institution"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(150))
    code = mapped_column(String(10))
    created_date = mapped_column(DateTime(timezone=True), default=func.now())    
    deleted_date = mapped_column(DateTime(timezone=True), nullable=True)
    collections = relationship("Collection")
    users: Mapped[List["User"]] = relationship(back_populates="institution")



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
    new_institution.users.add(admin_user)
    db.session.add(new_institution)
    db.session.commit()
    return new_institution


def delete_institution(institution_id):
    institution = db.session.get(Institution, institution_id)

    if institution:
        institution.deleted_date = datetime.datetime.now()
        db.session.commit()

    return True

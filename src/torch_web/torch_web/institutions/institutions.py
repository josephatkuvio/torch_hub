import datetime
from flask import flash
from typing import Collection, List
from sqlalchemy import func, Column, Integer, String, DateTime, ForeignKey, select
from sqlalchemy.orm import Mapped, relationship
from torch_web import Base, db


     

class Institution(Base):
    __tablename__ = "institution"
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    code = Column(String(10))
    created_date = Column(DateTime(timezone=True), default=func.now())    
    deleted_date = Column(DateTime(timezone=True), nullable=True)
    collections = relationship("Collection")
    #collections: Mapped[List["Collection"]] = relationship("Collection", back_populates="institution")    it didn't work 
    #users = relationship("torch_web.users.user.User", backref="institution")
    #users: Mapped[List["User"]] = relationship("User", back_populates="institution")          
    #users = relationship("User")    



def get_institutions():
    return db.session.scalars(select(Institution)).all()

def get_institution(id):
    inst = db.session.scalars(select(Institution).where(Institution.id == id)).one_or_none()
    return inst


def create_institution(name, code):
    if len(name) < 1:
        flash("Name is too short!", category="error")
        return None

    new_institution = Institution(name=name, code=code)
    db.session.add(new_institution)
    db.session.commit()
    return new_institution


def delete_institution(institution_id):
    institution = db.session.get(Institution, institution_id)

    if institution:
        institution.deleted_date = datetime.datetime.now()
        db.session.commit()

    return True

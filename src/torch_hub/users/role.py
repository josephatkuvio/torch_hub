from typing import List
from flask_security import RoleMixin, SQLAlchemyUserDatastore
from sqlalchemy import Column, Integer, String
from torch_hub.users import user
from torch_hub import db, Base


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


def get_roles() -> List[Role]:
    return Role.query.all()


def add_role(name, description):
    new_role = Role(name=name, description=description)
    db.session.add(new_role)
    db.session.commit()


def assign_role_to_user(user_id, role):
    user = User.query.get(user_id)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.add_role_to_user(user, role)
    db.session.commit()


def unassign_role_from_user(user_id, role):
    user = User.query.get(user_id)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.remove_role_from_user(user, role)
    db.session.commit()
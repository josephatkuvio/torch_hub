from typing import List
from flask_security import RoleMixin, SQLAlchemyUserDatastore
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import mapped_column
from torch_web.users import user
from torch_web import db, Base
from torch_web.users.user import User


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(80), unique=True)
    description = mapped_column(String(255))


def get_roles() -> List[Role]:
    return db.session.scalars(select(Role)).all()


def get_roles_by_name(name: str) -> List[Role]:
    return db.session.scalars(Role).filter_by(name=name).all()


def add_role(name, description):
    new_role = Role(name=name, description=description)
    db.session.add(new_role)
    db.session.commit()


def assign_role_to_user(user_id, role):
    user = user.get_user(user_id)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.add_role_to_user(user, role)
    db.session.commit()


def unassign_role_from_user(user_id, role):
    user = user.get_user(user_id)
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    user_datastore.remove_role_from_user(user, role)
    db.session.commit()

from flask_security import UserMixin
from torch_web import db, Base, mail
from sqlalchemy import Table, Integer, Column, String, Boolean, DateTime, ForeignKey, select
from sqlalchemy.orm import relationship, backref, joinedload, mapped_column
from flask_mail import Message
from flask import app

from torch_web.institutions.institutions import Institution


roles_users = Table(
    "roles_users",
    Base.metadata,
    mapped_column("user_id", Integer, ForeignKey("user.id")),
    mapped_column("role_id", Integer, ForeignKey("role.id")),
)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(150), unique=True)
    password = mapped_column(String(150))
    first_name = mapped_column(String(150))
    last_name = mapped_column(String(150))
    active = mapped_column(Boolean)
    confirmed_at = mapped_column(DateTime)
    institution_id = mapped_column(Integer, ForeignKey("institution.id"))
    institution: relationship("Institution", back_populates="users")
    fs_uniquifier = mapped_column(String(255), unique=True, nullable=False)
    roles = relationship(
        "Role", secondary=roles_users, backref=backref("users", lazy="dynamic")
    )


def get_users(institution_id):
    return db.session.scalars(select(User).options(joinedload(User.roles)).filter(institution_id=institution_id)).all()


#def get_user(user_id) -> User:
#    return db.session.get(User, user_id)

def get_user(id) -> User:
    return db.session.query(User).filter_by(id=id).first()


def save_user(user_id, first_name, last_name, institution_id):
    user = get_user(user_id)

    user.first_name = first_name
    user.last_name = last_name

    print(last_name)

    if institution_id is not None:
        institution = db.session.get(Institution, institution_id)
        user.institution_id = institution.id
        user.institution_code = institution.code
    elif user.institution_code is not None:
        institution = db.session.scalars(select(Institution).filter_by(code=user.institution_code)).first()
        user.institution_id = institution.id

    db.session.commit()


def toggle_user_active(user_id):
    user = get_user(user_id)
    user.active = 0 if user.active == 1 else 1

    db.session.commit()



def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config["FLASK_MAIL_DEFAULT_SENDER"],
        
    )
    mail.send(msg)


def remove_user(user_id):
    user = db.session.get(User, user_id)

    user.institution_id = None
    db.session.commit()

    return True
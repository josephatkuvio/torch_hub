from torch_web import db, mail
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from flask_mail import Message
from flask import current_app


from torch_web.model import Institution, User


def get_users(institution_id):
    return (
        db.session.scalars(
            select(User)
            .options(joinedload(User.roles))
            .join(User.institution)
            .filter(User.institution_id == institution_id)
        )
        .unique()
        .all()
    )


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
        sender= current_app.config["FLASK_MAIL_DEFAULT_SENDER"],
    )
    mail.send(msg)


def remove_user(user_id):
    user = db.session.get(User, user_id)

    user.institution_id = None
    db.session.commit()

    return True
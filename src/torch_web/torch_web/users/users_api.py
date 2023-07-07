import json
from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String, List, Nested
from flask import flash, jsonify, render_template, request, redirect, url_for
from flask_security import current_user, RegisterForm, roles_accepted
from wtforms import StringField
from torch_web.users import user, role
from torch_web.users.roles_api import RoleResponse
#from torch_web.model import User, Role
#from torch_web import db
from itsdangerous import URLSafeSerializer


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")


users_bp = APIBlueprint("users", __name__, url_prefix="/users")
auth_bp = APIBlueprint("auth", __name__, url_prefix="/_auth")


class SendInviteRequest(Schema):
    email = String()
    roles = Integer()


class UserResponse(Schema):
    id = Integer()
    email = String()
    first_name = String()
    last_name = String()
    institution_id = Integer()    
    roles = List(Nested(RoleResponse))


class UsersResponse(Schema):
    users = List(Nested(UserResponse))


class RemoveUserRequest(Schema):   
    institution_id = Integer() 
    collection_id = Integer()



@auth_bp.get("/login")
def login():
    return redirect("/login")


@auth_bp.get("/logout")
def logout():
    return redirect("/logout")


@auth_bp.get("/userinfo")
def userinfo():
    if not current_user.is_authenticated:
        return None
    
    claims = {}
    if current_user.roles:
        claims["http://schemas.microsoft.com/ws/2008/06/identity/claims/role"] = current_user.roles[0].name
    if current_user.institution:
        claims["institution_id"] = str(current_user.institution.id)
        claims["institution_name"] = current_user.institution.name
        claims["institution_code"] = current_user.institution.code
    if current_user.email:
        claims["email"] = current_user.email

    return {
        "Id": str(current_user.id),
        "UserName": current_user.first_name + " " + current_user.last_name,
        "Claims": claims
    }

#@auth_bp.post("/register")
#@users_bp.input(SendInviteRequest)
#@roles_accepted("admin", "supervisor")
#@users_bp.doc(operation_id='SendInvite')
#def register(data: dict):
#    email = data.get("email")
#    role_id = data.get("roles")
    
#    if not email:
#        abort(400, description="Email is required")

#    role = db.session.query(Role).get(role_id)

#    fs_uniquifier = "TEMPORARY_UNIQUE_VALUE"

#    user = User(email=email, roles=[role], institution_id=current_user.institution.id, fs_uniquifier=fs_uniquifier)
#    user.roles.append(role)
#    db.session.add(user)
#    db.session.commit()

#    registration_url = f"/register?email={email}"

#    subject = "Invitation to register on Torch"
#    html = render_template("templates/invite.html", registration_url=registration_url)
#    user.send_email(email, subject, html)    

#    return redirect("/register")





secret_key = "your-secret-key"
serializer = URLSafeSerializer(secret_key)

@auth_bp.post("/register")
@users_bp.input(SendInviteRequest)
@roles_accepted("admin", "supervisor")
@users_bp.doc(operation_id='SendInvite')
def register(request: SendInviteRequest):
    token = serializer.dumps({
        'email': request.email,
        'role': request.role,
        'institution_id': current_user.institution_id
    })

    registration_url = url_for('users_bp.register_user', token=token, _external=True)

    subject = "Invitation to register on Torch"
    html = render_template("templates/invite.html", registration_url=registration_url)
    user.send_email(request.email, subject, html)    

    return redirect("/register")

@users_bp.get("/register-user")    #check if should use users_bp or auth_bp
def register_user():
    token = request.args.get("token")
    try:
        data = serializer.loads(token)
        email = data['email']
        role = data['role']
        institution_id = data['institution_id']

        return render_template("security/register_user.html", email=email, role=role, institution_id=institution_id)
    except Exception:
        return "Invalid or expired token"



@users_bp.get("/")
@roles_accepted("admin")
@users_bp.output(UsersResponse)
@users_bp.doc(operation_id='GetUsers')
def users_getall():
    roles = role.get_roles()
    result = user.get_users(current_user.institution_id)
    return {
        "users": result
    }


@users_bp.get("/<userid>")
@users_bp.output(UserResponse)
@users_bp.doc(operation_id="GetUser")
def users_get(userid):
    result = user.get_user(userid)
    return result


@users_bp.post("/<userid>")
def users_post(userid):
    if request.method == "POST":

        user.save_user(
            userid,
            request.form.get("firstName"),
            request.form.get("lastName"),
            request.form.get("institutionid"),
        )

        flash("Updated successfully!", category="success")

    return users_get(userid)


@users_bp.post("/<userid>/active")
@roles_accepted("admin")
def deactivate_user(userid):
    user.toggle_user_active(userid)
    return jsonify({})


@users_bp.get("/<userid>/roles")
def user_add_role(userid):
    return render_template("addrolemodal.html", user=current_user, userid=userid)


@users_bp.post("/<userid>/roles")
@roles_accepted("admin")
def assign_role(userid):
    data = json.loads(request.data)
    user.assign_role_to_user(userid, data["role"])
    return jsonify({})


@users_bp.delete("/<userid>/roles")
@roles_accepted("admin")
def delete_role_user(userid):
    data = json.loads(request.data)
    print(data)
    user.unassign_role_from_user(userid, data["role"])
    return jsonify({})

@users_bp.delete("/<int:user_id>")
@users_bp.doc(operation_id='RemoveUser')
@roles_accepted("admin", "supervisor")
def user_remove(user_id):
    result = user.remove_user(user_id)
    if not result:
        return jsonify({"status": "error", "statusText": "Could not remove user."})

    return jsonify({"status": "ok"})
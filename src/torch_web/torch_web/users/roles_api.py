from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String
from flask import request
from flask_security import current_user, roles_required
from torch_web.users import role


roles_bp = APIBlueprint("roles", __name__, url_prefix="/roles")

class RolesResponse(Schema):
    id = Integer()
    name = String()
    



@roles_bp.get("/")
@roles_bp.output(RolesResponse)
@roles_bp.doc(operation_id='GetRoles')
@roles_required("admin", "supervisor")  
def roles_get():
    if current_user.has_role("admin"):
        roles = role.get_roles()
    elif current_user.has_role("supervisor"):
        roles = role.get_roles_by_name("basic")
    else:
        roles = []  

    return roles



@roles_bp.post("/")
@roles_required("admin")
def roles_post():
    role.add_role(request.form.get("name"), request.form.get("description"))
    return role.roles_get()

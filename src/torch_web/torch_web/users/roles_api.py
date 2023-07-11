from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String, List, Nested
from flask import request
from flask_security import current_user
from torch_web.users import role


roles_bp = APIBlueprint("roles", __name__, url_prefix="/roles")

class RoleResponse(Schema):
    id = Integer()
    name = String()
    
class RolesResponse(Schema):
    roles = List(Nested(RoleResponse))


@roles_bp.get("/")
@roles_bp.output(RolesResponse)
@roles_bp.doc(operation_id='GetRoles') 
def roles_get():
    result = role.get_roles()
    return {
        "roles": result
    }


@roles_bp.post("/")
def roles_post():
    role.add_role(request.form.get("name"), request.form.get("description"))
    return role.roles_get()

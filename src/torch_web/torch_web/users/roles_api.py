from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String, List, Nested
from flask import request
from flask_security import current_user, roles_accepted
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
@roles_accepted("admin", "supervisor")  
def roles_get():
    result = role.get_roles()
    return {
        "roles": result
    }

    #if current_user.has_role("admin"):
    #    roles = role.get_roles()
    #elif current_user.has_role("supervisor"):
    #    roles = role.get_roles_by_name("basic")
    #else:
    #    roles = []  



@roles_bp.post("/")
@roles_accepted("admin")
def roles_post():
    role.add_role(request.form.get("name"), request.form.get("description"))
    return role.roles_get()

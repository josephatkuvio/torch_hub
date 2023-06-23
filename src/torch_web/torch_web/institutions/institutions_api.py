import click

from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String, List, Nested, DateTime
from flask import jsonify, render_template, request
from flask_security import current_user
from torch_web.collections.collections_api import CollectionResponse
from torch_web.institutions import institutions
from rich.console import Console
from rich.table import Table


institutions_bp = APIBlueprint("institutions", __name__, url_prefix="/institutions")

class AddInstitutionRequest(Schema):
    name = String()
    code = String()

class InstitutionResponse(Schema):
    id = Integer()
    name = String()
    code = String()
    deleted_date = DateTime(timezone=True, nullable=True)
    collections = List(Nested(CollectionResponse))
    #users = List(Nested(UserResponse))   commented for now
class InstitutionsResponse(Schema):
    institutions = List(Nested(InstitutionResponse))

class DeleteInstitutionRequest(Schema):
    institution_id = Integer() 
    

@institutions_bp.get("/")
@institutions_bp.output(InstitutionsResponse)
@institutions_bp.doc(operation_id='GetInstitutions')
def institutions_get():
    result = institutions.get_institutions(institutions)
    return {
        "institutions": result
    }


@institutions_bp.get("/<int:institutionid>")
@institutions_bp.output(InstitutionResponse)
@institutions_bp.doc(operation_id='GetInstitution')
def collection_get(institutionid):
    result = institutions.get_institution(institutionid)
    return result


@institutions_bp.cli.command("list")
def list_institutions():
    result = institutions.get_institutions()
    table = Table(title="Current Institutions")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Code", style="green")

    for i in result:
        table.add_row(str(i.id), i.name, i.code)

    Console().print(table)
    

@institutions_bp.post("/")
@institutions_bp.input(AddInstitutionRequest)
@institutions_bp.output(InstitutionResponse)
@institutions_bp.doc(operation_id='AddInstitution')
def institutions_post(data):
    print(data)
    new_institution = institutions.create_institution(
        name=data['name'],
        code=data['code']
    )

    return new_institution


@institutions_bp.cli.command("create")
@click.argument("name")
@click.argument("code")
def create_institution(name, code):
    result = institutions.create_institution(name, code)
    Console().print(f'Institution [bold cyan]{name}[/bold cyan] created! ID is [bold magenta]{result.id}[/bold magenta].')


@institutions_bp.delete("/<int:institution_id>")
@institutions_bp.doc(operation_id='DeleteInstitution')
def delete(institution_id):
    result = institutions.delete_institution(institution_id)
    if not result:
        return jsonify({"status": "error", "statusText": "Institution not deleted."})

    return jsonify({"status": "ok"})


@institutions_bp.cli.command("delete")
@click.argument("id")
def delete_cli(id):
    institutions.delete_institution(id)
    Console().print(f'Institution ID [bold cyan]{id}[/bold cyan] deleted!')

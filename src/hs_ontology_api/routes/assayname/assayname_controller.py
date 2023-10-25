from flask import Blueprint, jsonify, current_app, request, make_response

from hs_ontology_api.routes.neo4j_logic import assaytype_name_get_logic

assayname_blueprint = Blueprint('assayname', __name__, url_prefix='/assayname')


@assayname_blueprint.route('', methods=['POST'])
def assayname_post():
    """Get the assaytypes with name and alt-names as found in the request body with key 'name'.
    This is a replacement for search-src endpoint of the same name.

    The 'application_context' is specified in the Request Data (see AssayNameRequest in ubkg-api-spec.yaml).
    If it is not specified it will default to 'HUBMAP'.

    The 'name' is also specified in the Request Data (again see AssayNameRequest in ubkg-api-spec.yaml).

    :rtype: Union[AssayTypePropertyInfo, Tuple[AssayTypePropertyInfo, int], Tuple[AssayTypePropertyInfo, int, Dict[str, str]]
    """
    if not request.is_json:
        return make_response("A JSON body with a 'Content-Type: application/json' header are required", 400)
    if 'name' not in request.json:
        return make_response('Request contains no "name" field', 400)
    application_context = "HUBMAP"
    if 'application_context' in request.json:
        application_context = request.json['application_context']
    req_name = request.json['name']
    alt_names: list = None
    if type(req_name) == list and len(req_name) > 0:
        name = req_name[0]
        if len(req_name) > 1:
            alt_names = req_name[1:]
    elif type(req_name) == str:
        name = req_name
    else:
        return make_response("The 'name' field is incorrectly specified "
                             "(see AssayNameRequest in ubkg-api-spec.yaml)", 400)
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = assaytype_name_get_logic(neo4j_instance, name, alt_names, application_context)
    if result is None:
        # JAS Oct 2023 changed from 400 to 404
        return make_response(f"No such assay_type {req_name}, even as alternate name", 404)
    return jsonify(result)

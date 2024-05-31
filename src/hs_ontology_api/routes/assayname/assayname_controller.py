from flask import Blueprint, jsonify, current_app, request, make_response

from hs_ontology_api.utils.neo4j_logic import assaytype_name_get_logic
from hs_ontology_api.utils.validate_parameters import validate_application_context, validate_active_status,\
    set_active_status_default

assayname_blueprint = Blueprint('assayname', __name__, url_prefix='/assayname')


@assayname_blueprint.route('', methods=['POST'])
def assayname_post():
    """Get the assaytypes with name and alt-names as found in the request body with key 'name'.
    This is a replacement for search-src endpoint of the same name.

    The 'application_context' is specified in the Request Data (see AssayNameRequest in ubkg-api-spec.yaml).
    If it is not specified it will default to 'HUBMAP'.

    The 'name' is also specified in the Request Data (again see AssayNameRequest in ubkg-api-spec.yaml).

    May 2024 - refactored to:
    1. Use the Cypher dataset query common to the datasets, assaytype, and assayname endpoints.
    2. Filter by active status.

    """
    if not request.is_json:
        return make_response("A JSON body with a 'Content-Type: application/json' header are required", 400)

    if 'name' not in request.json:
        return make_response('Request contains no "name" field', 400)

    # This endpoint should only be used in HUBMAP.
    application_context = "HUBMAP"
    if 'application_context' in request.json:
        application_context = request.json['application_context']

    err = validate_application_context(param_value=application_context)
    if err != 'ok':
        return make_response(err, 400)
    application_context = application_context.upper()

    # active status
    active_status = set_active_status_default()
    err = validate_active_status()
    if err != 'ok':
        return make_response(err, 400)

    print(f'active_status={active_status}')
    # This appears to replicate legacy logic originally intended to account for names that were composites--
    # e.g., ['AF', 'Image Pyramid']. The code below treats a list as a combination of data_type and alt_names,
    # which may not have been the original purpose of the composites. It's likely moot, as most of these composite
    # data types were refactored as part of "vis lifting". JAS

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
    result = assaytype_name_get_logic(neo4j_instance, name, alt_names, active_status, application_context)


    if result is None or result == []:
        # JAS Oct 2023 changed from 400 to 404
        # Not the standard custom 404, but replicates the original.
        return make_response(f"No such assay_type {req_name}, even as alternate name", 404)

    return jsonify(result)

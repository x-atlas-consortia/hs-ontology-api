# The assayname route replaces the equivalent legacy routes in the search-api.
# July 2024 - refactored to work with new UBKG assay class model.

from flask import Blueprint, jsonify, current_app, request, make_response
from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum,validate_required_parameters)
from hs_ontology_api.utils.neo4j_logic import assayclasses_get_logic
from hs_ontology_api.utils.listdict import remove_duplicate_dicts_from_list

assayname_blueprint = Blueprint('assayname', __name__, url_prefix='/assayname')


@assayname_blueprint.route('', methods=['POST'])
def assayname_post():
    """Get the assaytypes with name and alt-names as found in the request body with key 'name'.
    This is a replacement for search-src endpoint of the same name.

    The 'application_context' is specified in the Request Data (see AssayNameRequest in ubkg-api-spec.yaml).
    If it is not specified it will default to 'HUBMAP'.

    The 'name' is also specified in the Request Data (again see AssayNameRequest in ubkg-api-spec.yaml).

    """

    if not request.is_json:
        return make_response("A JSON request body with a 'Content-Type: application/json' header are required", 400)

    if 'name' not in request.json:
        return make_response('Request body contains no "name" field', 400)

    application_context = "HUBMAP"

    if 'application_context' in request.json:
        application_context = request.json['application_context']

    # Check for valid application context.
    val_enum = ['HUBMAP', 'SENNET']
    err = validate_parameter_value_in_enum(param_name='application_context', param_value=application_context,
                                               enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    # req_name = request.json['name']
    # The following is legacy code that attempted to handle composite and "alt-names", which have been deprecated.
    # alt_names: list = None
    # if type(req_name) == list and len(req_name) > 0:
        # name = req_name[0]
        # if len(req_name) > 1:
            # alt_names = req_name[1:]
    # elif type(req_name) == str:
        # name = req_name
    # else:
        # return make_response("The 'name' field is incorrectly specified "
                             # "(see AssayNameRequest in ubkg-api-spec.yaml)", 400)

    # Assume that only a single assay name is provided.
    name = request.json['name'][0]
    neo4j_instance = current_app.neo4jConnectionHelper.instance()

    result = assayclasses_get_logic(
        neo4j_instance, assaytype=name, context=application_context)

    if (result is None or result == []):
        # Empty result
        err = get_404_error_string(prompt_string=f"No results for "
                                                 f"specified parameters")
        return make_response(err, 404)

    # Build the legacy response from the new response.
    listresponse = []
    for r in result:
        assaytype = {}
        val = r.get('value')
        assaytype['name'] = val.get('assaytype')
        assaytype['primary'] = val.get('primary')
        assaytype['description'] = val.get('description')
        assaytype['vitessce-hints'] = val.get('vitessce_hints')
        # The vis-only and contains-pii properties have been deprecated.
        assaytype['vis-only'] = 'deprecated'
        assaytype['contains-pii'] = 'deprecated'
        listresponse.append(assaytype)

    # Remove duplicates. There will likely be both "non-DCWG" and "DCWG" rules for the same assaytype, for which the
    # subset used for assaytype response will contain duplicates.
    listunique = remove_duplicate_dicts_from_list(listinput=listresponse, indexval='name')

    return jsonify(listunique[0])


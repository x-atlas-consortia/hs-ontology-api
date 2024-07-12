# The assaytype routes replace the equivalent legacy routes in the search-api.
# July 2024 - refactored to work with new UBKG assay class model.

from flask import Blueprint, jsonify, current_app, request, make_response

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum,validate_required_parameters)

#from hs_ontology_api.utils.neo4j_logic import assaytype_get_logic, assaytype_name_get_logic
from hs_ontology_api.utils.neo4j_logic import assayclasses_get_logic
from hs_ontology_api.utils.listdict import remove_duplicate_dicts_from_list

assaytype_blueprint = Blueprint('assaytype', __name__, url_prefix='/assaytype')


@assaytype_blueprint.route('', methods=['GET'])
def route_assaytype_get():
    return assaytype_get()

@assaytype_blueprint.route('/<name>', methods=['GET'])
def route_assaytype_name_get(name):
    return assaytype_get(name)

def assaytype_get(name=None):
    """
    Returns information for the legacy assaytype and assaytype/{name} endpoints.
    :param name: corresponds to the assaytype
    """

    # Validate parameters.

    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['application_context', 'is_primary'])
    if err != 'ok':
        return make_response(err, 400)

    # Check for required parameters.
    application_context = request.args.get('application_context')
    # For assaytype, the default is HUBMAP.
    if application_context is None:
        application_context = 'HUBMAP'

    # Check for valid application context.
    val_enum = ['HUBMAP', 'SENNET']
    err = validate_parameter_value_in_enum(param_name='application_context', param_value=application_context,
                                           enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    # Check for valid parameter values.
    is_primary = request.args.get('is_primary')
    if is_primary is not None:
        is_primary = is_primary.lower()
        val_enum = ['true', 'false']
        err = validate_parameter_value_in_enum(param_name='is_primary', param_value=is_primary, enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = assayclasses_get_logic(
        neo4j_instance, assaytype=name, context=application_context)

    if (result is None or result == []):
        # Empty result
        err = get_404_error_string(prompt_string=f"No results for "
                                                 f"specified parameters")
        return make_response(err, 404)

    # Build the legacy response from the new response.
    listresponse=[]
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

    # The assaytype endpoint returns a list of objects that is the value of a key named 'result'.
    # The assaytype/{name} endpoint returns a single object.
    if len(listunique) ==1:
        return jsonify(listunique[0])
    else:
        return jsonify({'result':listunique})

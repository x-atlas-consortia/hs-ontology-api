from flask import Blueprint, jsonify, current_app, make_response,request, abort

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum, validate_required_parameters)
from hs_ontology_api.utils.neo4j_logic import assayclasses_get_logic

from urllib.parse import urlencode

assayclasses_blueprint = Blueprint('assayclasses_hs', __name__, url_prefix='/assayclasses')

def validate_param_as_boolean(param_name: str) ->str:
    """
    Evaluates a request parameter string as a boolean.

    :param param_name: name of the request parameter
    """

    val_enum = ['TRUE', 'FALSE']
    param_value = request.args.get(param_name)
    if param_value is not None:
        param_value = param_value.upper()

    return validate_parameter_value_in_enum(param_name=param_name, param_value=param_value, enum_list=val_enum)

def convert_param_to_boolean_string(param_name: str) -> str:
    """
    Converts a parameter string to a "boolean string"--i.e., "True" or "False"
    :param param_name: name of parameter
    """

    param_value = request.args.get(param_name)
    if param_value is None:
        return 'False'

    param_value = param_value.upper()
    if param_value == 'TRUE':
        return 'True'
    else:
        return 'False'

@assayclasses_blueprint.route('', methods=['GET'])
def assayclasses_expand_get():
    return assayclasses_get()
@assayclasses_blueprint.route('/<name>', methods=['GET'])
def assayclasses_name_expand_get(name):
    return assayclasses_get(name=name)


def assayclasses_get(name=None):
    """Returns information on a set of HuBMAP or SenNet assay classifications, rule-based dataset "kinds" that are
    in the testing rules json, with options to filter the list to those with specific property values.
    Filters are additive (i.e., boolean AND)

    October 2024 - Request parameters added for:
    provide_hierarchy_info: whether to display hierarchical information on the dataset type
    provide_measurement_assay_codes: whether to display the measurement assay codes

    """
    # Validate parameters.

    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['application_context', 'process_state', 'assaytype',
                                                              'provide-hierarchy-info'])
    if err != 'ok':
        return make_response(err, 400)

    # Check for required parameters.
    err = validate_required_parameters(required_parameter_list=['application_context'])
    if err != 'ok':
        return make_response(err, 400)
    application_context = request.args.get('application_context')

    # Check for valid application context. The parameter is case-insensitive, but any error should return the
    # value provided in the request.
    val_enum = ['HUBMAP','SENNET']
    err = validate_parameter_value_in_enum(param_name='application_context', param_value=application_context.upper(),
                                           enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)
    application_context = application_context.upper()

    # Check for valid parameter values.
    process_state = request.args.get('process_state')
    if process_state is not None:
        process_state = process_state.lower()
        val_enum=['primary','derived','epic']
        err = validate_parameter_value_in_enum(param_name='process_state',param_value=process_state,enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)

    # Filter by assaytype.
    # If this is for the endpoint that filters by assay class, then ignore filtering by assaytype.
    # (The endpoint that filters by assay class assumes a single response, and assaytype is not unique for assay
    # classes).
    assaytype = request.args.get('assaytype')
    if assaytype is not None and name is not None:
       assaytype = None

    # Oct 2024 - filter response for dataset type hierarchy.
    err = validate_param_as_boolean('provide-hierarchy-info')
    if err != 'ok':
        return make_response(err, 400)
    provide_hierarchy_info = convert_param_to_boolean_string('provide-hierarchy-info')


    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = assayclasses_get_logic(
        neo4j_instance, assayclass=name, process_state=process_state, assaytype=assaytype,
        context=application_context, provide_hierarchy_info=provide_hierarchy_info)

    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f"No results for "
                                                 f"specified parameters")
        return make_response(err, 404)

    if len(result) == 1:
        return jsonify(result[0])
    else:
        return jsonify(result)

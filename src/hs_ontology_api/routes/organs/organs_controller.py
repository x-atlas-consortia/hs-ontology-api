from flask import Blueprint, jsonify, current_app, make_response,request

from hs_ontology_api.utils.neo4j_logic import get_organ_types_logic
from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum, validate_required_parameters)

organs_blueprint = Blueprint('organs_hs', __name__, url_prefix='/organs')


@organs_blueprint.route('', methods=['GET'])
def get_organ_types():

    # Check for required parameters.
    err = validate_required_parameters(required_parameter_list=['application_context'])
    if err != 'ok':
        return make_response(err, 400)
    application_context = request.args.get('application_context')

    # Check for valid application context. The parameter is case-insensitive.
    val_enum = ['HUBMAP', 'SENNET']
    err = validate_parameter_value_in_enum(param_name='application_context', param_value=application_context.upper(),
                                           enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    application_context = application_context.upper()

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(get_organ_types_logic(neo4j_instance, application_context.upper()))


@organs_blueprint.route('by-code', methods=['GET'])
def get_organ_by_code():

    # Check for required parameters.
    err = validate_required_parameters(required_parameter_list=['application_context'])
    if err != 'ok':
        return make_response(err, 400)
    application_context = request.args.get('application_context')

    # Check for valid application context. The parameter is case-insensitive.
    val_enum = ['HUBMAP', 'SENNET']
    err = validate_parameter_value_in_enum(param_name='application_context', param_value=application_context.upper(),
                                           enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    application_context = application_context.upper()

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    data: list = get_organ_types_logic(neo4j_instance, application_context.upper())
    result: dict = {}
    for item in data:
        result[item['rui_code']] = item['term'].strip()
    return jsonify(result)




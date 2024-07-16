from flask import Blueprint, jsonify, current_app, make_response,request

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum, validate_required_parameters)
from hs_ontology_api.utils.neo4j_logic import assayclasses_get_logic

assayclasses_blueprint = Blueprint('assayclasses_hs', __name__, url_prefix='/assayclasses')

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

    """
    # Validate parameters.

    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['application_context','is_primary','assaytype'])
    if err != 'ok':
        return make_response(err, 400)

    # Check for required parameters.
    err = validate_required_parameters(required_parameter_list=['application_context'])
    if err != 'ok':
        return make_response(err, 400)
    application_context = request.args.get('application_context')

    # Check for valid application context.
    val_enum = ['HUBMAP','SENNET']
    err = validate_parameter_value_in_enum(param_name='application_context', param_value=application_context, enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    # Check for valid parameter values.
    is_primary = request.args.get('is_primary')
    if is_primary is not None:
        is_primary = is_primary.lower()
        val_enum=['true','false']
        err = validate_parameter_value_in_enum(param_name='is_primary',param_value=is_primary,enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)

    assaytype = request.args.get('assaytype')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = assayclasses_get_logic(
            neo4j_instance, assayclass=name, is_primary=is_primary, assaytype=assaytype, context=application_context)

    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f"No results for "
                                                 f"specified parameters")
        return make_response(err, 404)


    return jsonify(result)

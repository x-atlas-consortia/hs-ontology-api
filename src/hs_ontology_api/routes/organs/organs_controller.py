from flask import Blueprint, jsonify, current_app, request, make_response

# from ubkg_api.common_routes.validate import validate_application_context
from hs_ontology_api.utils.validate_parameters import validate_application_context

from hs_ontology_api.utils.neo4j_logic import get_organ_types_logic

organs_blueprint = Blueprint('organs_hs', __name__, url_prefix='/organs')


@organs_blueprint.route('', methods=['GET'])
def get_organ_types():

    # May 2024 - refactored to use new standard methodology for validating application context.

    # Validate required application context.
    application_context = request.args.get('application_context')
    err = validate_application_context(param_value=application_context)
    if err != 'ok':
        return make_response(err, 400)
    application_context = application_context.upper()

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(get_organ_types_logic(neo4j_instance, application_context.upper()))


@organs_blueprint.route('by-code', methods=['GET'])
def get_organ_by_code():

    # May 2024 - refactored to use new standard methodology for validating application context.

    # Validate required application context.
    application_context = request.args.get('application_context')
    err = validate_application_context(param_value=application_context)
    if err != 'ok':
        return make_response(err, 400)
    application_context = application_context.upper()

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    data: list = get_organ_types_logic(neo4j_instance, application_context)
    result: dict = {}
    for item in data:
        result[item['rui_code']] = item['term'].strip()
    return jsonify(result)




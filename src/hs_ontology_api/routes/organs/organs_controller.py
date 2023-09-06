from flask import Blueprint, jsonify, current_app

from ubkg_api.common_routes.validate import validate_application_context

from ..neo4j_logic import get_organ_types_logic

organs_blueprint = Blueprint('organs_hs', __name__, url_prefix='/organs')


@organs_blueprint.route('', methods=['GET'])
def get_organ_types():
    application_context = validate_application_context()
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(get_organ_types_logic(neo4j_instance, application_context.upper()))


@organs_blueprint.route('by-code', methods=['GET'])
def get_organ_by_code():
    application_context = validate_application_context()
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    data: list = get_organ_types_logic(neo4j_instance, application_context.upper())
    result: dict = {}
    for item in data:
        result[item['rui_code']] = item['term'].strip()
    return jsonify(result)




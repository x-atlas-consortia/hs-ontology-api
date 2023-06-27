from flask import Blueprint, jsonify, current_app

from ubkg_api.routes.validate import validate_application_context

organs_blueprint = Blueprint('organs_hs', __name__, url_prefix='/organs')


@organs_blueprint.route('', methods=['GET'])
def get_organ_types():
    application_context = validate_application_context()
    return jsonify(current_app.neo4jManager.get_organ_types(application_context.upper()))


@organs_blueprint.route('by-code', methods=['GET'])
def get_organ_by_code():
    application_context = validate_application_context()
    data: list = current_app.neo4jManager.get_organ_types(application_context.upper())
    result: dict = {}
    for item in data:
        result[item['rui_code']] = item['term'].strip()
    return jsonify(result)




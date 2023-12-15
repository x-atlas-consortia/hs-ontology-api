# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_descriptions_get_logic


field_descriptions_blueprint = Blueprint('field-descriptions', __name__, url_prefix='/field-descriptions')

@field_descriptions_blueprint.route('', methods=['GET'])
def field_descriptions_expand_get():
    """Returns detailed information on field descriptions.

    :rtype: Union[List[FieldDescription]]

    """
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_descriptions_get_logic(neo4j_instance)
    if result is None or result == []:
        # Empty result
        return make_response(f"No legacy field descriptions.", 404)
    return jsonify(result)
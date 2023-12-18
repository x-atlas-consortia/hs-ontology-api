# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_types_get_logic


field_types_blueprint = Blueprint('field-types', __name__, url_prefix='/field-types')

@field_types_blueprint.route('', methods=['GET'])
def field_types_expand_get():
    """Returns detailed information on field types.

    :rtype: Union[List[FieldType]]

    """
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_types_get_logic(neo4j_instance)
    if result is None or result == []:
        # Empty result
        return make_response(f"No legacy field types.", 404)
    return jsonify(result)
# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_assays_get_logic


field_assays_blueprint = Blueprint('field-assays', __name__, url_prefix='/field-assays')

@field_assays_blueprint.route('', methods=['GET'])
def field_assays_expand_get():
    """Returns detailed information on field assays.

    :rtype: Union[List[FieldAssay]]

    """
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_assays_get_logic(neo4j_instance)
    if result is None or result == []:
        # Empty result
        return make_response(f"No field to assay associations.", 404)
    return jsonify(result)
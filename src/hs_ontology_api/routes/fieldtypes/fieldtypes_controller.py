# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_types_get_logic
from hs_ontology_api.utils.field_error_string import get_error_string


field_types_blueprint = Blueprint('field-types', __name__, url_prefix='/field-types')


def field_types_get(name=None):
    """Returns detailed information on field types.

    :rtype: Union[List[FieldType]]

    """
    # Check for invalid parameters
    for req in request.args:
        if req not in ['mapping_source', 'type_source', 'type']:
            return make_response(f"Invalid parameter: '{req}'", 400)

    # Validate mapping source.
    mapping_source = request.args.get('mapping_source')
    if mapping_source is not None:
        mapping_source = mapping_source.upper()
        if mapping_source not in ['HMFIELD', 'CEDAR']:
            return make_response(f"Invalid value for mapping source parameter: '{mapping_source}'", 400)

    # Validate type source.
    type_source = request.args.get('type_source')
    if type_source is not None:
        type_source = type_source.upper()
        if type_source not in ['HMFIELD', 'XSD']:
            return make_response(f"Invalid value for type source parameter: '{type_source}'", 400)

    type = request.args.get('type')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_types_get_logic(neo4j_instance, field_name=name, mapping_source=mapping_source,
                                   type_source=type_source, type=type)
    if result is None or result == []:
        # Empty result
        err = get_error_string(field_name=name, prompt_string='No field type associations')
        if type is not None:
            err = err + ' Call field-types-info for a list of available field data types.'
        return make_response(err, 404)
    return jsonify(result)


@field_types_blueprint.route('', methods=['GET'])
def field_types_expand_get():
    return field_types_get()


@field_types_blueprint.route('/<name>', methods=['GET'])
def field_types_name_expand_get(name):
    return field_types_get(name=name)

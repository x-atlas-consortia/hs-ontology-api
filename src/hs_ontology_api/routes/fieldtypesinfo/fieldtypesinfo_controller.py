# coding: utf-8
# JAS January 2024
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_types_info_get_logic
from ubkg_api.utils.http_error_string import get_404_error_string, validate_query_parameter_names, \
    validate_parameter_value_in_enum

field_types_info_blueprint = Blueprint('field-types-info', __name__, url_prefix='/field-types-info')


def field_types_info_get():
    """Returns unique list of information on field types.

    :rtype: Union[List[FieldType]]

    """

    # Validate parameters
    err = validate_query_parameter_names(['type_source'])
    if err != 'ok':
        return make_response(err, 400)

    # Validate type source.
    type_source = request.args.get('type_source')
    if type_source is not None:
        type_source = type_source.upper()
        val_enum = ['HMFIELD', 'XSD']
        err = validate_parameter_value_in_enum(param_name='type_source', param_value=type_source, enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_types_info_get_logic(neo4j_instance, type_source=type_source)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string='No field types')
        return make_response(err, 404)
    return jsonify(result)


@field_types_info_blueprint.route('', methods=['GET'])
def field_types_expand_get():
    return field_types_info_get()

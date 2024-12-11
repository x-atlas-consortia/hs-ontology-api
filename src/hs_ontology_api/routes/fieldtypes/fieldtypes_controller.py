# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_types_get_logic
from ubkg_api.utils.http_error_string import get_404_error_string, validate_query_parameter_names, \
    validate_parameter_value_in_enum


field_types_blueprint = Blueprint('field-types', __name__, url_prefix='/field-types')


def field_types_get(name=None):
    """Returns detailed information on field types.

    :rtype: Union[List[FieldType]]

    """
    # Validate parameter names.
    err = validate_query_parameter_names(['mapping_source', 'type_source', 'type'])
    if err != 'ok':
        return make_response(err, 400)

    # Validate mapping source.
    mapping_source = request.args.get('mapping_source')
    if mapping_source is not None:
        val_enum = ['HMFIELD', 'CEDAR']
        mapping_source = mapping_source.upper()
        err = validate_parameter_value_in_enum(param_name='mapping_source', param_value=mapping_source,
                                               enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)

    # Validate type source.
    type_source = request.args.get('type_source')
    if type_source is not None:
        val_enum = ['HMFIELD', 'XSD']
        type_source = type_source.upper()
        err = validate_parameter_value_in_enum(param_name='type_source', param_value=type_source,
                                               enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)

    type = request.args.get('type')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_types_get_logic(neo4j_instance, field_name=name, mapping_source=mapping_source,
                                   type_source=type_source, type=type)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string='No field type associations')
        if type is not None:
            err = err + ' Call the field-types-info endpoint for a list of available field data types. ' \
                        'Refer to the SmartAPI documentation for this endpoint for more information.'
        return make_response(err, 404)
    return jsonify(result)


@field_types_blueprint.route('', methods=['GET'])
def field_types_expand_get():
    return field_types_get()


@field_types_blueprint.route('/<name>', methods=['GET'])
def field_types_name_expand_get(name):
    return field_types_get(name=name)

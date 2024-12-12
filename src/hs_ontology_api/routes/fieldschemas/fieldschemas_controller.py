# coding: utf-8
# JAS January 2024
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_schemas_get_logic
from ubkg_api.utils.http_error_string import get_404_error_string, validate_query_parameter_names, \
    validate_parameter_value_in_enum

field_schemas_blueprint = Blueprint('field-schemas', __name__, url_prefix='/field-schemas')


def field_schemas_get(name=None):
    """Returns detailed information on field schema associations.

    :rtype: Union[List[FieldSchema]]

    """
    # Validate parameters
    err = validate_query_parameter_names(['source', 'schema'])
    if err != 'ok':
        return make_response(err, 400)

    # Validate source.
    source = request.args.get('source')
    if source is not None:
        source = source.upper()
        val_enum = ['HMFIELD', 'CEDAR']
        err = validate_parameter_value_in_enum(param_name='source', param_value=source, enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)

    schema = request.args.get('schema')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_schemas_get_logic(neo4j_instance, field_name=name, mapping_source=source, schema=schema)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string='No field schema associations')
        return make_response(err, 404)
    return jsonify(result)


@field_schemas_blueprint.route('', methods=['GET'])
def field_schemas_expand_get():
    return field_schemas_get()


@field_schemas_blueprint.route('/<name>', methods=['GET'])
def field_schemas_name_expand_get(name):
    return field_schemas_get(name=name)

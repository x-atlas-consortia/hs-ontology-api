# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_descriptions_get_logic
from ubkg_api.utils.http_error_string import get_404_error_string, validate_query_parameter_names, \
    validate_parameter_value_in_enum
# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

field_descriptions_blueprint = Blueprint('field-descriptions', __name__, url_prefix='/field-descriptions')


def field_descriptions_get(name=None):
    """Returns detailed information on field descriptions.
    :param name: field name (used in the field-descriptions/<name> route)
    :rtype: Union[List[FieldDescription]]

    """
    # Validate parameter names.
    err = validate_query_parameter_names(['source'])
    if err != 'ok':
        return make_response(err, 400)

    # Validate parameters with values from limited set.
    source = request.args.get('source')
    if source is not None:
        source = source.upper()
    val_enum = ['HMFIELD', 'CEDAR']
    err = validate_parameter_value_in_enum(param_name='source', param_value=source, enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_descriptions_get_logic(neo4j_instance, field_name=name, definition_source=source)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string='No field descriptions')
        return make_response(err, 404)

    # March 2025
    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)

@field_descriptions_blueprint.route('', methods=['GET'])
def field_descriptions_expand_get():
    return field_descriptions_get()


@field_descriptions_blueprint.route('/<name>', methods=['GET'])
def field_descriptions_name_expand_get(name):
    return field_descriptions_get(name=name)

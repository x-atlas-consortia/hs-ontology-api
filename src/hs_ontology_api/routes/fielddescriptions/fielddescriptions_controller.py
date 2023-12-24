# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_descriptions_get_logic

def get_error_string(field_name=None):
    """
    Formats an error string for a 404 response, accounting for optional parameters.

    :param field_name: field name (used in the field-assays/<name> route)
    :return: string
    """

    listerr = []
    if field_name is not None:
        listerr.append(f'name={field_name}')

    err = 'No field descriptions'
    if len(listerr) > 0:
        err = err + ' with parameters: ' + '; '.join(listerr) + '.'

    return err

def field_descriptions_get(name=None):
    """Returns detailed information on field descriptions.
    :param name: field name (used in the field-descriptions/<name> route)
    :rtype: Union[List[FieldDescription]]

    """

    for req in request.args:
        if req not in ['source']:
            return make_response(f"Invalid parameter: '{req}'", 400)

    source = request.args.get('source')
    if source is not None:
        source = source.upper()
        if not source in ['HMFIELD', 'CEDAR']:
            return make_response(f"Invalid value for source parameter: '{source}'", 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_descriptions_get_logic(neo4j_instance, field_name=name, definition_source=source)
    if result is None or result == []:
        # Empty result
        err = get_error_string(field_name=name)
        return make_response(err, 404)

    return jsonify(result)

field_descriptions_blueprint = Blueprint('field-descriptions', __name__, url_prefix='/field-descriptions')

@field_descriptions_blueprint.route('', methods=['GET'])
def field_descriptions_expand_get():
    return field_descriptions_get()

@field_descriptions_blueprint.route('/<name>', methods=['GET'])
def field_descriptions_name_expand_get(name):
    return field_descriptions_get(name=name)


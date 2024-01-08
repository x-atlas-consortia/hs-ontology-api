# coding: utf-8
# JAS January 2024
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_entities_get_logic
from hs_ontology_api.utils.http_error_string import get_404_error_string,validate_query_parameter_names


field_entities_blueprint = Blueprint('field-entities', __name__, url_prefix='/field-entities')


def field_entities_get(name=None):
    """Returns detailed information on field entities.

    :rtype: Union[List[FieldEntity]]

    """

    # Validate parameters
    err = validate_query_parameter_names(['source', 'entity'])
    if err != 'ok':
        return make_response(err, 400)


    # Validate mapping source.
    source = request.args.get('source')
    if source is not None:
        source = source.upper()
        if source not in ['HMFIELD', 'HUBMAP']:
            return make_response(f"Invalid value for source parameter: '{source}'", 400)


    entity = request.args.get('entity')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_entities_get_logic(neo4j_instance, field_name=name, source=source,
                                   entity=entity)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string='No field type associations')
        if type is not None:
            err = err + ' Call field-types-info for a list of available field data types.'
        return make_response(err, 404)
    return jsonify(result)


@field_entities_blueprint.route('', methods=['GET'])
def field_entities_expand_get():
    return field_entities_get()


@field_entities_blueprint.route('/<name>', methods=['GET'])
def field_entities_name_expand_get(name):
    return field_entities_get(name=name)

# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_assays_get_logic
from hs_ontology_api.utils.http_error_string import get_404_error_string, validate_query_parameter_names

field_assays_blueprint = Blueprint('field-assays', __name__, url_prefix='/field-assays')


def field_assays_get(name=None):
    """Returns detailed information on associations between metadata fields and assay
        :param name: field name (used in the field-assays/<name> route)
        :rtype: Union[List[FieldAssay]]

    """

    # Get optional filtering parameters:
    # assay_identifier - legacy identifier for assay dataset from field_assays.yaml.
    #                    Can be a data_type, alt-name, or description.
    # data_type - legacy data_type, used in ingestion workflows
    # dataset_type - "soft assay" dataset type, used by the Rules Engine

    # Validate parameters
    err = validate_query_parameter_names(['assay_identifier', 'data_type', 'dataset_type'])
    if err != 'ok':
        return make_response(err, 400)

    assay_identifier = request.args.get('assay_identifier')
    data_type = request.args.get('data_type')
    dataset_type = request.args.get('dataset_type')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_assays_get_logic(neo4j_instance, field_name=name, assay_identifier=assay_identifier,
                                    data_type=data_type, dataset_type=dataset_type)

    iserr = False
    if result is None or result == []:
        iserr = True
    else:
        # Check for no assay associations.
        assays = result[0].get('assays')
        iserr = len(assays) == 0

    if iserr:
        # Empty result
        err = get_404_error_string(prompt_string='No field assay associations')
        return make_response(err, 404)

    return jsonify(result)


@field_assays_blueprint.route('', methods=['GET'])
def field_assays_expand_get():
    return field_assays_get()


@field_assays_blueprint.route('/<name>', methods=['GET'])
def field_assays_name_expand_get(name):
    return field_assays_get(name=name)

# coding: utf-8
# JAS December 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import field_assays_get_logic

field_assays_blueprint = Blueprint('field-assays', __name__, url_prefix='/field-assays')


def get_error_string(field_name=None, assay_identifier=None, data_type=None, dataset_type=None):
    """
    Formats an error string for a 404 response, accounting for optional parameters.

    :param field_name: field name (used in the field-assays/<name> route)
    :param assay_identifier: optional assay identifier
    :param data_type: optional data_type
    :param dataset_type: optional dataset_type
    :return: string
    """

    listerr = []
    if field_name is not None:
        listerr.append(f'name={field_name}')

    if assay_identifier is not None:
        listerr.append(f'assay_identifier={assay_identifier}')

    if data_type is not None:
        listerr.append(f'data_type={data_type}')

    if dataset_type is not None:
        listerr.append(f'dataset_type={dataset_type}')

    err = 'No field to assay associations'
    if len(listerr) > 0:
        err = err + ' with parameters: ' + '; '.join(listerr) + '.'

    return err


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

    for req in request.args:
        if req not in ['assay_identifier','data_type','dataset_type']:
            return make_response(f"Invalid parameter: '{req}'", 400)

    assay_identifier = request.args.get('assay_identifier')
    data_type = request.args.get('data_type')
    dataset_type = request.args.get('dataset_type')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = field_assays_get_logic(neo4j_instance, field_name=name, assay_identifier=assay_identifier,
                                    data_type=data_type, dataset_type=dataset_type)
    if result is None or result == []:
        # Empty result
        err = get_error_string(field_name=name, assay_identifier=assay_identifier,
                               data_type=data_type, dataset_type=dataset_type)
        return make_response(err, 404)
    return jsonify(result)


@field_assays_blueprint.route('', methods=['GET'])
def field_assays_expand_get():
    return field_assays_get()


@field_assays_blueprint.route('/<name>', methods=['GET'])
def field_assays_name_expand_get(name):
    return field_assays_get(name=name)

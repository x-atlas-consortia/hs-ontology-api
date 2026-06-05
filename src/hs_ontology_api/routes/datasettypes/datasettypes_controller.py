from flask import Blueprint, jsonify, current_app, make_response,request

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum, validate_required_parameters)
from hs_ontology_api.utils.neo4j_logic import dataset_types_get_logic
# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

datasettypes_blueprint = Blueprint('datasettypes_hs', __name__, url_prefix='/dataset-types')

@datasettypes_blueprint.route('', methods=['GET'])
def datasettypes_expand_get():
    return datasettypes_get()

@datasettypes_blueprint.route('/<dataset_type_code>', methods=['GET'])
def datasettypes_dataset_type_get(dataset_type_code):
    return datasettypes_get(dataset_type_code=dataset_type_code)

@datasettypes_blueprint.route('/<dataset_type_code>/<modality_code>', methods=['GET'])
def datasettypes_dataset_type_modality_get(dataset_type_code, modality_code):
    return datasettypes_get(dataset_type_code=dataset_type_code, modality_code=modality_code)

@datasettypes_blueprint.route('/<dataset_type_code>/<modality_code>/<analyte_code>', methods=['GET'])
def datasettypes_dataset_type_modality_analyte_get(dataset_type_code, modality_code, analyte_code):
    return datasettypes_get(dataset_type_code=dataset_type_code, modality_code=modality_code, analyte_code=analyte_code)

def datasettypes_get(dataset_type_code=None, modality_code=None, analyte_code=None):
    """
    Returns information on a set of HuBMAP or SenNet assay classifications, rule-based dataset "kinds" that are
    in the testing rules json, with options to filter the list to those with specific property values.
    Filters are additive (i.e., boolean AND).

    """
    # Validate parameters.

    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['application_context','is_externally_processed'])
    if err != 'ok':
        return make_response(err, 400)

    # Check for valid isepic. The parameter is case-insensitive.

    isepic = request.args.get('is_externally_processed')
    if isepic is None:
        isepic = 'false'
    else:
        val_enum = ['TRUE', 'FALSE']
        err = validate_parameter_value_in_enum(param_name='is_externally_processed', param_value=isepic.upper(),
                                           enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)
        isepic = isepic.lower()


    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = dataset_types_get_logic(
        neo4j_instance,
        dataset_type_code=dataset_type_code,
        modality_code=modality_code,
        analyte_code=analyte_code,
        isepic=isepic)

    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f"No results for "
                                                 f"specified parameters")
        return make_response(err, 404)

    # Result is either a list with one element or a single item.
    # Redirect to S3 if large.
    if len(result) == 1:
        resp = result[0]
    else:
        resp = result
    return redirect_if_large(resp=resp)

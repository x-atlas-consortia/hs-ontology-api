from flask import Blueprint, jsonify, current_app, make_response,request

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum, validate_required_parameters)
from hs_ontology_api.utils.neo4j_logic import modalities_get_logic, modalities_valueset_get_logic

# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

modalities_blueprint = Blueprint('modalities_hs', __name__, url_prefix='/modalities')


@modalities_blueprint.route('', methods=['GET'])
def modalities_expand_get():
    return modalities_get()

@modalities_blueprint.route('/<modality_code>', methods=['GET'])
def modalities_dataset_type_get(modality_code):
    if modality_code.lower()=='valueset':
        return modalities_valueset_get()
    else:
        return modalities_get(modality_code=modality_code)

@modalities_blueprint.route('/<modality_code>/<dataset_type_code>', methods=['GET'])
def modalities_modality_dataset_type_get(modality_code, dataset_type_code):
    return modalities_get(modality_code=modality_code, dataset_type_code=dataset_type_code)

@modalities_blueprint.route('/<modality_code>/<dataset_type_code>/<analyte_code>', methods=['GET'])
def modalities_modality_dataset_type_analyte_get(modality_code, dataset_type_code,  analyte_code):
    return modalities_get(modality_code=modality_code, dataset_type_code=dataset_type_code, analyte_code=analyte_code)

def modalities_valueset_get():
    """
    Returns a simple valueset of modality codes.
    """
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = modalities_valueset_get_logic(neo4j_instance)

    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f"No results for "
                                                 f"specified parameters")
        return make_response(err, 404)

    # Redirect to S3 if large.
    return redirect_if_large(resp=result)

def modalities_get(modality_code=None, dataset_type_code=None, analyte_code=None):
    """
    Returns information on a set of SenNet modalities, with options to filter the list to those with specific property values.
    Filters are additive (i.e., boolean AND).

    """
    # Validate parameters.

    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['is_externally_processed'])
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
    result = modalities_get_logic(
        neo4j_instance,
        modality_code=modality_code,
        dataset_type_code=dataset_type_code,
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

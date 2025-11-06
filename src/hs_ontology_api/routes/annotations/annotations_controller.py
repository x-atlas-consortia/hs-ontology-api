from flask import Blueprint, jsonify, current_app, make_response, request
from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum, validate_required_parameters)
from hs_ontology_api.utils.neo4j_logic import annotations_get_logic, annotation_organ_levels_get_logic

# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large
from ubkg_api.utils.http_error_string import get_404_error_string

annotations_blueprint = Blueprint('annotations', __name__, url_prefix='/annotations')

@annotations_blueprint.route('/<ids>', methods=['GET'])
def get_annotations_id_route(ids):
    return get_annotations(ids=ids)
@annotations_blueprint.route('', methods=['GET'])
def get_annotations_route():
    return get_annotations()
def get_annotations(ids=None):
    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['sab'])
    if err != 'ok':
        return make_response(err, 400)

    # Check for required parameters.
    err = validate_required_parameters(required_parameter_list=['sab'])
    if err != 'ok':
        return make_response(err, 400)
    sab = request.args.get('sab')

    # Check for valid sab. The parameter is case-insensitive, but any error should return the
    # value provided in the request.
    val_enum = ['AZ', 'STELLAR', 'DCTH', 'PAZ', 'RIBCA', 'VCCF']
    err = validate_parameter_value_in_enum(param_name='sab', param_value=sab.upper(),
                                           enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    listids = []
    if ids is not None:
        listids = ids.split(',')

    annids = []

    # Pad numeric ids with zeroes to 7 characters.
    for i in listids:
        if i.isnumeric():
            annids.append(f'{int(i):07d}')
        else:
            if i.strip() != '':
                annids.append(i)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = annotations_get_logic(neo4j_instance, sab=sab, ids=annids)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No annotations with identifiers')
        return make_response(err, 404)

    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)

@annotations_blueprint.route('/organ-levels', methods=['GET'])
def get_annotation_organ_levels_route():
    return get_annotation_organ_levels()
@annotations_blueprint.route('/<ids>/organ-levels', methods=['GET'])
def get_annotation_organ_levels_id_route(ids):
    return get_annotation_organ_levels(ids)

def get_annotation_organ_levels(ids=None):

    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['sab'])
    if err != 'ok':
        return make_response(err, 400)

    sab = request.args.get('sab')
    if sab is not None:
        sab = sab.upper()

    # Check for valid sab. The parameter is case-insensitive, but any error should return the
    # value provided in the request.
    val_enum = ['AZ', 'STELLAR', 'DCTH', 'PAZ', 'RIBCA', 'VCCF']


    err = validate_parameter_value_in_enum(param_name='sab', param_value=sab,
                                           enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    listids = []
    if ids is not None:
        listids = ids.split(',')

    organ_level_ids = []

    # Pad numeric ids with zeroes to 7 characters.
    for i in listids:
        if i.isnumeric():
            organ_level_ids.append(f'{int(i):07d}')
        else:
            if i.strip() != '':
                organ_level_ids.append(i)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = annotation_organ_levels_get_logic(neo4j_instance, sab=sab, ids=organ_level_ids)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No annotation organ levels with identifiers')
        return make_response(err, 404)

    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)
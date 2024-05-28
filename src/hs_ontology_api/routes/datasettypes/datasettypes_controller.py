from flask import Blueprint, jsonify, current_app, request,  make_response
from ubkg_api.utils.http_error_string import validate_required_parameters,validate_query_parameter_names,\
    get_404_error_string,validate_parameter_value_in_enum

# MAY 2024 Use common utilities from ubkg-api.
from hs_ontology_api.utils.neo4j_logic import dataset_types_get_logic

dataset_types_blueprint = Blueprint('dataset_types', __name__, url_prefix='/dataset-types')

@dataset_types_blueprint.route('', methods=['GET'])
def dataset_types_expand_get():
    return dataset_types_get()


@dataset_types_blueprint.route('/<type>', methods=['GET'])
def dataset_types_name_expand_get(type):
    return dataset_types_get(dataset_type=type)


def dataset_types_get(dataset_type=None):

    """
       Returns information on a set of HuBMAP or SenNet dataset types, with options to filter the list to those with
    specific property values. Filters are additive (i.e., boolean AND).
    """

    # Validate parameter names.
    err = validate_query_parameter_names(['application_context', 'dataset_type', 'dataset_type_active'])
    if err != 'ok':
        return make_response(err, 400)

    # Validate required application_context.
    err = validate_required_parameters(required_parameter_list=['application_context'])
    if err != 'ok':
        return make_response(err, 400)

    # case-insensitive
    application_context = request.args.get('application_context').upper()
    val_enum = ['HUBMAP', 'SENNET']
    err = validate_parameter_value_in_enum(param_name='application_context', param_value=application_context,
                                           enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    # dataset_type_active's default is active.
    val_enum = ['active', 'inactive']
    dataset_type_active = request.args.get('dataset_type_active')
    # May 2024 Return all dataset types by default.
    #if dataset_type_active is None:
        #dataset_type_active = 'active'
    #else:
    if dataset_type_active is not None:
        dataset_type_active = dataset_type_active.lower()
    err = validate_parameter_value_in_enum(param_name='dataset_type_active', param_value=dataset_type_active,
                                           enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    dataset_type = request.args.get('dataset_type')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = dataset_types_get_logic(neo4j_instance, dataset_type=dataset_type,
                                     dataset_type_active=dataset_type_active, application_context=application_context)

    iserr = result is None or result == {}
    if not iserr:
        checklist = result.get('dataset_types')
        iserr = checklist == []

    if iserr:
        err = get_404_error_string(prompt_string='No dataset types')
        return make_response(err, 404)

    return jsonify(result)
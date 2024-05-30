from flask import Blueprint, jsonify, current_app, request,  make_response

# MAY 2024 Deprecated
# from ubkg_api.common_routes.validate import validate_application_context

# MAY 2024 Use common utilities from ubkg-api.
from ubkg_api.utils.http_error_string import validate_required_parameters,validate_query_parameter_names,\
    get_404_error_string,validate_parameter_value_in_enum

from hs_ontology_api.utils.neo4j_logic import dataset_get_logic

from hs_ontology_api.utils.validate_parameters import validate_application_context, validate_active_status, \
    set_active_status_default

datasets_blueprint = Blueprint('datasets_hs', __name__, url_prefix='/datasets')


@datasets_blueprint.route('', methods=['GET'])
def dataset_get():

    """
    MAY 2024 - Refactored to use standard methodology for ubkg-api/hs-ontology-api endpoints.

    Returns information on a set of HuBMAP or SenNet dataset types, with options to filter the list to those with
    specific property values. Filters are additive (i.e., boolean AND).
    """

    # Validate parameter names.
    err = validate_query_parameter_names(['application_context','data_type','description','alt_name','primary',
                                          'contains_pii','vis-only','vitessce_hint','dataset_provider',
                                          'dataset_type', 'active_status'])
    if err != 'ok':
        return make_response(err, 400)

    # Validate required application context.
    application_context = request.args.get('application_context')
    err = validate_application_context(param_value=application_context)
    if err != 'ok':
        return make_response(err, 400)
    application_context = application_context.upper()

    data_type = request.args.get('data_type')
    description = request.args.get('description')
    alt_name = request.args.get('alt_name')

    # Parameters with true/false option.
    val_enum = ['true', 'false']
    primary = request.args.get('primary')
    if primary is not None:
        primary = primary.lower()
    err = validate_parameter_value_in_enum(param_name='primary', param_value=primary, enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    contains_pii = request.args.get('contains_pii')
    if contains_pii is not None:
        contains_pii = contains_pii.lower()
    err = validate_parameter_value_in_enum(param_name='contains_pii', param_value=contains_pii, enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    vis_only = request.args.get('vis-only')
    if vis_only is not None:
        vis_only = vis_only.lower()
    err = validate_parameter_value_in_enum(param_name='vis-only', param_value=vis_only, enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    vitessce_hint = request.args.get('vitessce_hint')

    val_enum = ['iec', 'external', 'lab']
    dataset_provider = request.args.get('dataset_provider')
    if dataset_provider is not None:
        dataset_provider = dataset_provider.lower()
    err = validate_parameter_value_in_enum(param_name='dataset_provider', param_value=dataset_provider, enum_list=val_enum)
    if err != 'ok':
        return make_response(err, 400)

    dataset_type = request.args.get('dataset_type')

    # active status
    active_status = set_active_status_default()
    err = validate_active_status()
    if err != 'ok':
        return make_response(err, 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = dataset_get_logic(neo4j_instance, data_type=data_type, description=description,
                               alt_name=alt_name, primary=primary, contains_pii=contains_pii, vis_only=vis_only,
                               vitessce_hint=vitessce_hint, dataset_provider=dataset_provider,
                               dataset_type=dataset_type, active_status=active_status,
                               application_context=application_context)

    if result is None or result == {}:
        # Empty result
        err = get_404_error_string(prompt_string='No datasets')
        if type is not None:

            err = err + 'Refer to the SmartAPI documentation for this endpoint for more information.'
        return make_response(err, 404)

    return jsonify(result)

def dataset_get_old():
    # May 2024 replaced with new standard methodology.

    """Returns information on a set of HuBMAP or SenNet dataset types, with options to filter the list to those with specific property values. Filters are additive (i.e., boolean AND)

    :query application_context: Required filter to indicate application context.
    :type application_context: str
    :param data_type: Optional filter for data_type
    :type data_type: str
    :param description: Optional filter for display name. Use URL-encoding (space &#x3D; %20).
    :type description: str
    :param alt_name: Optional filter for a single element in the alt-names list--i.e., return datasets for which alt-names includes a value that matches the parameter. Although the field is named &#39;alt-names&#39;, the parameter uses &#39;alt_name&#39;. Use URL-encoding (space &#x3D; %20)
    :type alt_name: str
    :param primary: Optional filter to filter to primary (true) or derived (false) assay.
    :type primary: str
    :param contains_pii: Optional filter for whether the dataset contains Patient Identifying Information (PII). Although the field is named &#39;contains-pii&#39;, use &#39;contains_pii&#39; as an argument.
    :type contains_pii: str
    :param vis_only: Optional filter for whether datasets are visualization only (true). Although the field is named &#39;vis-only&#39;, use &#39;vis_only&#39; as an argument.
    :type vis_only: str
    :param vitessce_hint: Optional filter for a single element in the vitessce_hint list--i.e., return datasets for which vitessce_hints includes a value that matches the parameter. Although the field is named &#39;vitessce-hints&#39;, use &#39;vitessce_hint&#39; as an argument.
    :type vitessce_hint: str
    :param dataset_provider: Optional filter to identify the dataset provider - IEC (iec)  or external (lab)
    :type dataset_provider: str

    :rtype: Union[List[DatasetPropertyInfo], Tuple[List[DatasetPropertyInfo], int], Tuple[List[DatasetPropertyInfo], int, Dict[str, str]]
    """

    application_context = validate_application_context()
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(dataset_get_logic(neo4j_instance, request.args.get('data_type'),
                                     request.args.get('description'),request.args.get('alt_name'),
                                     request.args.get('primary'), request.args.get('contains_pii'),
                                     request.args.get('vis_only'), request.args.get('vitessce_hint'),
                                     request.args.get('dataset_provider'),application_context))



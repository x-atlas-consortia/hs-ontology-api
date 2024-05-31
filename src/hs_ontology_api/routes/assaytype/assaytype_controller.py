from flask import Blueprint, jsonify, current_app, request, make_response

#from ubkg_api.common_routes.validate import validate_application_context

from hs_ontology_api.utils.neo4j_logic import assaytype_get_logic, assaytype_name_get_logic
from ubkg_api.utils.http_error_string import validate_required_parameters,validate_query_parameter_names,\
    get_404_error_string,validate_parameter_value_in_enum

from hs_ontology_api.utils.validate_parameters import validate_application_context, validate_active_status, \
    set_active_status_default

assaytype_blueprint = Blueprint('assaytype', __name__, url_prefix='/assaytype')


@assaytype_blueprint.route('', methods=['GET'])
def assaytype_get():
    """
    Get all assaytypes without query parameter.
    ?primary=true Only get those where record['primary'] == True
    ?primary=false Only get those where record['primary'] == False

    :return:
    """
    primary: bool = request.args.get('primary', default=None)
    if primary is not None:
        primary = primary.lower() == 'true'

    # Validate required application context.
    application_context = request.args.get('application_context')
    err = validate_application_context(param_value=application_context)
    if err != 'ok':
        return make_response(err, 400)
    application_context = application_context.upper()

    # active status
    active_status = set_active_status_default()
    err = validate_active_status(param_value=active_status)
    if err != 'ok':
        return make_response(err, 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(assaytype_get_logic(neo4j_instance=neo4j_instance, primary=primary,
                                       active_status=active_status, application_context=application_context))


@assaytype_blueprint.route('/<name>', methods=['GET'])
def assaytype_name_get(name):
    """Get all assaytypes with name.
    This is a replacement for search-src endpoint of the same name.

    :param name: AssayType name
    :type name: str
    :param application_context: Filter to indicate application context
    :type application_context: str
    :param active_status: Filter for active status
    """
    # application_context = validate_application_context()

    # Validate required application context.
    application_context = request.args.get('application_context')
    err = validate_application_context(param_value=application_context)
    if err != 'ok':
        return make_response(err, 400)
    application_context = application_context.upper()

    # active status
    active_status = set_active_status_default()
    err = validate_active_status(param_value=active_status)
    if err != 'ok':
        return make_response(err, 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = assaytype_name_get_logic(neo4j_instance, name=name, alt_names=None,
                                      active_status=active_status, application_context=application_context)

    if result == []:
        # Add information on active_status parameter to legacy custom 404.
        # return make_response(f"No such assay_type {name}", 404)
        err = get_404_error_string(prompt_string=f'No such assay_type {name}')
        return err

    return jsonify(result)

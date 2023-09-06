from flask import Blueprint, jsonify, current_app, request, make_response

from ubkg_api.common_routes.validate import validate_application_context

from hs_ontology_api.routes.neo4j_logic import assaytype_get_logic, assaytype_name_get_logic

assaytype_blueprint = Blueprint('assaytype', __name__, url_prefix='/assaytype')


@assaytype_blueprint.route('', methods=['GET'])
def assaytype_get():
    """
    Get all of the assaytypes without query parameter.
    ?primary=true Only get those where record['primary'] == True
    ?primary=false Only get those where record['primary'] == False

    :return:
    """
    primary: bool = request.args.get('primary', default=None)
    if primary is not None:
        primary = primary.lower() == 'true'
    application_context = validate_application_context()
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(assaytype_get_logic(neo4j_instance, primary, application_context))


@assaytype_blueprint.route('/<name>', methods=['GET'])
def assaytype_name_get(name):
    """Get all of the assaytypes with name.
    This is a replacement for search-src endpoint of the same name.

    :param name: AssayType name
    :type name: str
    :param application_context: Filter to indicate application context
    :type application_context: str

    :rtype: Union[AssayTypePropertyInfo, Tuple[AssayTypePropertyInfo, int], Tuple[AssayTypePropertyInfo, int, Dict[str, str]]
    """
    application_context = validate_application_context()
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = assaytype_name_get_logic(neo4j_instance, name, None, application_context)
    if result is None:
        return make_response(f"No such assay_type {name}", 400)
    return jsonify(result)

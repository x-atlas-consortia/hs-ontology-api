from flask import Blueprint, jsonify, current_app, make_response,request

from ubkg_api.common_routes.validate import validate_application_context
from ubkg_api.utils.http_error_string import get_404_error_string
from hs_ontology_api.utils.neo4j_logic import assayclasses_get_logic

assayclasses_blueprint = Blueprint('assayclasses_hs', __name__, url_prefix='/assayclasses')

@assayclasses_blueprint.route('', methods=['GET'])
def assayclasses_expand_get():
    return assayclasses_get()
@assayclasses_blueprint.route('/<name>', methods=['GET'])
def assayclasses_name_expand_get(name):
    return assayclasses_get(name=name)


def assayclasses_get(name=None):
    """Returns information on a set of HuBMAP or SenNet assay classifications, rule-based dataset "kinds" that are
    in the testing rules json, with options to filter the list to those with specific property values.
    Filters are additive (i.e., boolean AND)

    """

    application_context = validate_application_context()
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = assayclasses_get_logic(
            neo4j_instance,assayclass=name, context=application_context)

    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f"No results for "
                                                 f"specified parameters")
        return make_response(err, 404)


    return jsonify(result)

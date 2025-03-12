# coding: utf-8
# JAS September 2023
from flask import Blueprint, jsonify, current_app, make_response
from hs_ontology_api.utils.neo4j_logic import proteindetail_get_logic
# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

proteins_blueprint = Blueprint('proteins', __name__, url_prefix='/proteins')

@proteins_blueprint.route('/<id>', methods=['GET'])
def proteins_id_expand_get(id=None):
    """Returns detailed information on a single protein.

    :rtype: Union[List[GeneDetail]]

    The following types of identifiers can be used in the list:
    1. UniProtKB ID
    2. UniProtKB Entry Names (e.g., MMRN1_HUMAN)

    """

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = proteindetail_get_logic(neo4j_instance, id)
    if result is None or result == []:
        # Empty result
        return make_response(f"No information for protein with UniProtKB identifier {id}.", 404)

    # March 2025
    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)
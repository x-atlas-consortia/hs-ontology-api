# coding: utf-8
# JAS September 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from ..neo4j_logic import genedetail_get_logic


genedetail_blueprint = Blueprint('genedetail', __name__, url_prefix='/gene')

@genedetail_blueprint.route('', methods=['GET'])
def genedetail_expand_get():
    return make_response('The /gene endpoint should specify a single HGNC gene identifier--e.g., /gene/MMRN1.', 400)


@genedetail_blueprint.route('/<id>', methods=['GET'])
def genedetail_id_expand_get(id=None):
    """Returns detailed information on a single gene.

    :rtype: Union[List[GeneDetail]]

    The following types of identifiers can be used in the list:
    1. HGNC numeric IDs (e.g., 7178)
    2. HGNC approved symbols (e.g., MMRN1)
    3. HGNC previous symbols (e.g., MMRN)
    4. HGNC aliases (e.g., ECM)
    5. names (approved name, previous name, alias name).

    Because exact matches would be required, it is unlikely that names would be useful criteria.

    """

    if id =='' or id is None:
        return make_response('The /gene endpoint should specify a HGNC gene identifier--e.g., /gene/MMRN1.',400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = genedetail_get_logic(neo4j_instance, id)
    if result is None or result == []:
        return make_response(f"No information for gene with HGNC identifier {id}.", 400)
    return jsonify(result)
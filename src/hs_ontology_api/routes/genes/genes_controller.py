# coding: utf-8
# JAS September 2023
from flask import Blueprint, jsonify, current_app, make_response
from hs_ontology_api.utils.neo4j_logic import genedetail_get_logic


genes_blueprint = Blueprint('genes', __name__, url_prefix='/genes')

@genes_blueprint.route('/<id>', methods=['GET'])
def genes_id_expand_get(id=None):
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
        # Missing ID parameter in URL
        return make_response('The /genes endpoint must specify a HGNC gene identifier--e.g., /genes/MMRN1.',400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = genedetail_get_logic(neo4j_instance, id)
    if result is None or result == []:
        # Empty result
        return make_response(f"No information for gene with HGNC identifier {id}.", 404)
    return jsonify(result)
# coding: utf-8
# JAS September 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from ..neo4j_logic import genedetail_get_logic


genedetail_blueprint = Blueprint('genedetail', __name__, url_prefix='/gene_detail')

@genedetail_blueprint.route('', methods=['GET'])
def genedetail_expand_get():
    """Returns a unique list of genes.

    :rtype: Union[List[GeneDetail]]

    The following types of identifiers can be used in the list:
    1. HGNC numeric IDs (e.g., 7178)
    2. HGNC approved symbols (e.g., MMRN1)
    3. HGNC previous symbols (e.g., MMRN)
    4. HGNC aliases (e.g., ECM)
    5. names (approved name, previous name, alias name).

    Because exact matches would be required, it is unlikely that names would be useful criteria.

    """

    # Obtain the list of gene IDs from parameters.
    id = request.args.get('id')
    if id =='' or id is None:
        return make_response('The id parameter is blank. It should specify a gene identifier.',400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(genedetail_get_logic(neo4j_instance, id))
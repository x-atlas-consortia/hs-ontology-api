# coding: utf-8
# JAS September 2023
from flask import Blueprint, jsonify, current_app, request
from ..neo4j_logic import genedetail_post_logic

genedetail_blueprint = Blueprint('genes', __name__, url_prefix='/genes')


@genedetail_blueprint.route('', methods=['POST'])
def genedetail_expand_post():
    """Returns a unique list of genes.

    :rtype: Union[List[GeneDetail]]

    The request body is an array of HGNC identifiers.
    The following types of identifiers can be used in the list:
    1. HGNC numeric IDs (e.g., 7178)
    2. HGNC approved symbols (e.g., MMRN1)
    3. HGNC previous symbols (e.g., MMRN)
    4. HGNC aliases (e.g., ECM)
    5. names (approved name, previous name, alias name).

    Because exact matches would be required, it is unlikely that names would be useful criteria.
    If no criteria are specified, return information on all HGNC genes.

    """
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(genedetail_post_logic(neo4j_instance, request.get_json()))
# coding: utf-8
# JAS September 2023
from flask import Blueprint, jsonify, current_app, make_response
from hs_ontology_api.utils.neo4j_logic import genedetail_get_logic, gene_get_logic
# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large
from ubkg_api.utils.http_error_string import get_404_error_string

genes_blueprint = Blueprint('genes', __name__, url_prefix='/genes')

@genes_blueprint.route('/<ids>/detail', methods=['GET'])
def genes_id_detail_expand_get(ids=None):
    """Returns detailed information on a single gene, including annotation mappings.

    :rtype: Union[List[GeneDetail]]

    The following types of identifiers can be used in the list:
    1. HGNC numeric IDs (e.g., 7178)
    2. HGNC approved symbols (e.g., MMRN1)
    3. HGNC previous symbols (e.g., MMRN)
    4. HGNC aliases (e.g., ECM)
    5. names (approved name, previous name, alias name).

    Because exact matches would be required, it is unlikely that names would be useful criteria.

    """

    geneids = ids.split(',')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = genedetail_get_logic(neo4j_instance, geneids)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No genes with identifiers')
        return make_response(err, 404)

    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)

@genes_blueprint.route('/<ids>', methods=['GET'])
def genes_id_expand_get(ids=None):
    """
    OCTOBER 2025
    Returns detailed information for genes that match a set of gene identifiers

    The following types of identifiers can be used in the list:
    1. HGNC numeric IDs (e.g., 7178)
    2. HGNC approved symbols (e.g., MMRN1)
    3. HGNC previous symbols (e.g., MMRN)
    4. HGNC aliases (e.g., ECM)
    5. names (approved name, previous name, alias name).

    Because exact matches would be required, it is unlikely that names would be useful criteria.

    """

    geneids = ids.split(',')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = gene_get_logic(neo4j_instance, geneids)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No genes with identifiers')
        return make_response(err, 404)

    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)
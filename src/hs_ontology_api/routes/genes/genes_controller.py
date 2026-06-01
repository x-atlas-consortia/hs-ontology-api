# coding: utf-8
# JAS September 2023
from flask import Blueprint, jsonify, current_app, make_response, request
from hs_ontology_api.utils.neo4j_logic import genedetail_get_logic, gene_get_logic
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum, validate_required_parameters)


genes_blueprint = Blueprint('genes', __name__, url_prefix='/genes')

@genes_blueprint.route('/<ids>/detail', methods=['GET'])
def genes_id_detail_expand_get(ids=None):

    """
    Returns detailed information on a set of genes, including applicable
    annotation mappings.

    Currently applies to human genes only.

    The following types of identifiers can be used in the list:

    Human genes
    1. HGNC numeric IDs (e.g., 7178)
    2. HGNC approved symbols (e.g., MMRN1)
    3. HGNC previous symbols (e.g., MMRN)
    4. HGNC aliases (e.g., ECM)
    5. names (approved name, previous name, alias name).


    Because exact matches would be required, it is unlikely that names would be useful criteria.

    """

    geneids = ids.split(',')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = genedetail_get_logic(neo4j_instance, geneids=geneids)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No genes with identifiers')
        return make_response(err, 404)

    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)

@genes_blueprint.route('/<ids>', methods=['GET'])
def genes_id_expand_get(ids=None):
    """

    Returns reference information for genes that match a set of gene identifiers

    The following types of identifiers can be used in the list:

    Human genes
    1. HGNC numeric IDs (e.g., 7178)
    2. HGNC approved symbols (e.g., MMRN1)
    3. HGNC previous symbols (e.g., MMRN)
    4. HGNC aliases (e.g., ECM)
    5. names (approved name, previous name, alias name).

    Mouse genes
    1. MGI numeric IDs
    2. MGI approved symbols

    Because exact matches would be required, it is unlikely that names would be useful criteria.

    """

    err = validate_query_parameter_names(parameter_name_list=['organism'])
    if err != 'ok':
        return make_response(err, 400)

    # Check for valid parameter values.
    organism = request.args.get('organism')
    if organism is not None:
        organism = organism.lower()
        val_enum = ['human', 'mouse']
        err = validate_parameter_value_in_enum(param_name='organism', param_value=organism,
                                                   enum_list=val_enum)
        if err != 'ok':
            return make_response(err, 400)

    geneids = ids.split(',')

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = gene_get_logic(neo4j_instance, geneids=geneids, organism=organism)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No genes with identifiers')
        return make_response(err, 404)

    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)
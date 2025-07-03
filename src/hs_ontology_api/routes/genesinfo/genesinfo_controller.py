# coding: utf-8
# JAS October 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import genelist_get_logic,genelist_count_get_logic
import math
# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum, validate_required_parameters)


genesinfo_blueprint = Blueprint('genes-info', __name__, url_prefix='/genes-info')

@genesinfo_blueprint.route('', methods=['GET'])
def geneslist() -> list[str]:

    neo4j_instance = current_app.neo4jConnectionHelper.instance()

    # Obtain a list of genes that the Cells API identifies as being in datasets.
    # Until the response from the Cells API improves, use the UBKG.
    # return jsonify(ontcells.genes_from_cells())

    # JUNE 2025 - Validation
    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['page','genes_per_page', 'starts_with'])
    if err != 'ok':
        return make_response(err, 400)

    # Obtain parameters.
    page = request.args.get('page')
    genes_per_page = request.args.get('genes_per_page')
    starts_with = request.args.get('starts_with')
    if starts_with is None:
        starts_with = ''

    # Validate and set defaults for genes_per_page.
    if genes_per_page is None:
        genes_per_page = '10'
    if not genes_per_page.isnumeric():
        return make_response(f'The value for parameter genes_per_page ({genes_per_page}) must be numeric.', 400)
    if int(genes_per_page) <= 0:
        return (make_response(f'The value for parameter genes_per_page ({genes_per_page}) must be greater than zero.', 400))

    # Escape apostrophes and double quotes.
    starts_with = starts_with.replace("'", "\'").replace('"', "\'")
    # Obtain the total count of genes, considering the filter starts_with.
    gene_count = genelist_count_get_logic(neo4j_instance, starts_with)

    if gene_count == 0:
        return make_response(f"There are no genes with HGNC symbols that start with '{starts_with}'.", 404)

    # Default values for page.
    # Case: No parameter specified.
    if page is None:
        page = '1'
    # Case: 0.
    # It is likely that a UI would supply 0 as a page parameter.
    if page == '0':
        page = '1'

    # Calculate the total number of (filtered) pages.
    total_pages = str(math.ceil(int(gene_count) / int(genes_per_page)))

    # Translation for cases "last" or "first"
    if page == 'last':
        page = str(int(total_pages))
    if page == 'first':
        page = '1'

    # Parameter validation.
    if not page.isnumeric():
        return make_response(f"The value for parameter page ({page}) must be either a number >=0 or the "
                             f"words 'first' or 'last'.", 400)
    if int(page) < 0:
        return make_response(f'The value for parameter page ({page}) must be >= 0', 400)

    if int(page) > int(total_pages):
        page = str(int(total_pages))

    # Obtain results.
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = genelist_get_logic(neo4j_instance,
                                page=page,
                                total_pages=total_pages,
                                genes_per_page=genes_per_page,
                                starts_with=starts_with,
                                gene_count=gene_count)

    # March 2025
    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)
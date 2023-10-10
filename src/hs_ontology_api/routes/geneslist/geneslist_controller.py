# coding: utf-8
# JAS October 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from ..neo4j_logic import genesfromubkg_get_logic,genesfromubkg_count_get_logic

geneslist_blueprint = Blueprint('geneslist', __name__, url_prefix='/gene_list')

@geneslist_blueprint.route('', methods=['GET'])
def geneslist() -> list[str]:

    neo4j_instance = current_app.neo4jConnectionHelper.instance()

    # Obtain a list of genes that the Cells API identifies as being in datasets.
    # return jsonify(ontcells.genes_from_cells())

    # Obtain a list of genes.
    # Obtain pagination parameters.
    page = request.args.get('page')

    # Validate and set default for LIMIT in neo4j query.
    genesperpage = request.args.get('genesperpage')
    if genesperpage is None:
        genesperpage = '10'

    if not genesperpage.isnumeric():
        return make_response(f'Page genesperpage={genesperpage} is not numeric', 400)
    if int(genesperpage) < 0:
        return make_response(f'Parameter genesperpage={genesperpage} cannot be negative', 400)

    # The SKIP parameter in neo4j is 0-based, but the UI expectation is that pages
    # are 1-based--i.e., the assumption is that a UI would not show a "page 0" option.
    # The following conversion will render the results of page=0 and page=1 identical.
    # This could be confusing for direct calls that use page=0 and page=1.

    # Note: this is done in the controller instead of in the neo4j_logic module
    # because of the need to validate the parameter.

    # Default values.
    if page is None:
        page = '1'
    if page == '0':
        page = '1'

    # Obtain the total count of genes.
    gene_count = genesfromubkg_count_get_logic(neo4j_instance)
    # Calculate the total number of pages
    total_pages = str(int(gene_count)//int(genesperpage) - 1)

    if page == 'last':
        page = str(int(total_pages) + 1)
    if page == 'first':
        page = '1'

    # Parameter validation.
    if not page.isnumeric():
        return make_response(f'Parameter page={page} is not numeric', 400)
    if int(page) < 0:
        return make_response(f'Parameter page={page} cannot be negative', 400)

    # Convert from 1-based paging (UI expectation) to 0-based paging (for SKIP).
    page = str(int(page) - 1)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(genesfromubkg_get_logic(neo4j_instance, page=page, total_pages=total_pages, genesperpage=genesperpage))
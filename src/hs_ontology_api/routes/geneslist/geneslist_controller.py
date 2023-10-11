# coding: utf-8
# JAS October 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from ..neo4j_logic import genelist_get_logic,genelist_count_get_logic

geneslist_blueprint = Blueprint('geneslist', __name__, url_prefix='/gene_list')

@geneslist_blueprint.route('', methods=['GET'])
def geneslist() -> list[str]:

    neo4j_instance = current_app.neo4jConnectionHelper.instance()

    # Obtain a list of genes that the Cells API identifies as being in datasets.
    # Until the response from the Cells API improves, use the UBKG.
    # return jsonify(ontcells.genes_from_cells())

    # Obtain pagination parameters.
    page = request.args.get('page')
    genesperpage = request.args.get('genesperpage')

    # Validate and set defaults for genesperpage.
    if genesperpage is None:
        genesperpage = '10'
    if not genesperpage.isnumeric():
        return make_response(f'Page genesperpage={genesperpage} is not numeric', 400)
    if int(genesperpage) < 0:
        return make_response(f'Parameter genesperpage={genesperpage} cannot be negative', 400)

    # Default values for page.
    # Case: No parameter specified.
    if page is None:
        page = '1'
    # Case: 0.
    # It is likely that a UI would supply 0 as a page parameter.
    if page == '0':
        page = '1'

    # Case: "last" or "first"
    # Obtain the total count of genes.
    gene_count = genelist_count_get_logic(neo4j_instance)
    # Calculate the total number of pages.
    total_pages = str(int(gene_count) // int(genesperpage))

    if page == 'last':
        page = str(int(total_pages))
    if page == 'first':
        page = '1'
    # Parameter validation.
    if not page.isnumeric():
        return make_response(f'Parameter page={page} is not numeric', 400)
    if int(page) < 0:
        return make_response(f'Parameter page={page} cannot be negative', 400)

    # Obtain results.
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(genelist_get_logic(neo4j_instance, page=page, total_pages=total_pages, genesperpage=genesperpage))
# coding: utf-8
# JAS October 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from ..neo4j_logic import genelist_get_logic,genelist_count_get_logic
import math

geneslist_blueprint = Blueprint('geneslist', __name__, url_prefix='/genes')

@geneslist_blueprint.route('', methods=['GET'])
def geneslist() -> list[str]:

    neo4j_instance = current_app.neo4jConnectionHelper.instance()

    # Obtain a list of genes that the Cells API identifies as being in datasets.
    # Until the response from the Cells API improves, use the UBKG.
    # return jsonify(ontcells.genes_from_cells())

    # Obtain parameters.
    page = request.args.get('page')
    genesperpage = request.args.get('genesperpage')
    starts_with = request.args.get('starts_with')
    if starts_with is None:
        starts_with = ''

    # Validate and set defaults for genesperpage.
    if genesperpage is None:
        genesperpage = '10'
    if not genesperpage.isnumeric():
        return make_response(f'The value for parameter genesperpage ({genesperpage}) must be numeric.', 400)
    if int(genesperpage) <= 0:
        return (make_response(f'The value for parameter genesperpage ({genesperpage}) must be greater than zero.', 400))

    # Obtain the total count of genes, considering the filter starts_with.
    gene_count = genelist_count_get_logic(neo4j_instance, starts_with)
    if gene_count == 0:
        return make_response(f'There are no genes with HGNC symbols that start with \'{starts_with}\'.', 404)

    # Default values for page.
    # Case: No parameter specified.
    if page is None:
        page = '1'
    # Case: 0.
    # It is likely that a UI would supply 0 as a page parameter.
    if page == '0':
        page = '1'

    # Calculate the total number of (filtered) pages.
    total_pages = str(math.ceil(int(gene_count) / int(genesperpage)))

    # Translation for cases "last" or "first"
    print(f'total_pages={total_pages}')
    if page == 'last':
        page = str(int(total_pages))
    if page == 'first':
        page = '1'

    # Parameter validation.
    if not page.isnumeric():
        return make_response(f'The value for parameter page ({page}) must be either a number >=0 or the words \'first\' or \'last\'.', 400)
    if int(page) < 0:
        return make_response(f'The value for parameter page ({page}) must be >= 0', 400)

    if int(page) > int(total_pages):
        page = str(int(total_pages))

    # Obtain results.
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(genelist_get_logic(neo4j_instance, page=page, total_pages=total_pages, genesperpage=genesperpage, starts_with=starts_with, gene_count=gene_count))
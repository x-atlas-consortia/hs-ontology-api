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
        return make_response(f'The value for parameter genesperpage ({genesperpage}) must be numeric.', 400)
    if int(genesperpage) <= 0:
        return (make_response(f'The value for parameter genesperpage ({genesperpage}) must be greater than zero.', 400))

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

    # To support type-ahead
    starts_with = request.args.get('starts_with')
    if not starts_with is None:
        page = '1'
    else:
        starts_with = ''

    # Parameter validation.
    if not page.isnumeric():
        return make_response(f'The value for parameter page ({page}) must be either a number >=0 or the words \'first\' or \'last\'.', 400)
    if int(page) < 0:
        return make_response(f'The value for parameter page ({page}) must be >= 0', 400)

    if int(page) > int(total_pages):
        return make_response(f'The value for parameter page ({page}) is greater than the total number of pages ({total_pages}) of size {genesperpage}.')



    # Obtain results.
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(genelist_get_logic(neo4j_instance, page=page, total_pages=total_pages, genesperpage=genesperpage, starts_with=starts_with))
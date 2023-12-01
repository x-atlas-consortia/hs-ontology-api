# coding: utf-8
# JAS November 2023
from flask import Blueprint, jsonify, current_app, request, make_response
from hs_ontology_api.utils.neo4j_logic import celltypelist_count_get_logic, celltypelist_get_logic
import math

celltypesinfo_blueprint = Blueprint('celltypes-info', __name__, url_prefix='/celltypes-info')


@celltypesinfo_blueprint.route('', methods=['GET'])
def celltypeslist() -> list[str]:

    neo4j_instance = current_app.neo4jConnectionHelper.instance()

    # Obtain a list of cell types that the Cells API identifies as being in datasets.
    # Until the response from the Cells API improves, use the UBKG.
    # return jsonify(ontcells.genes_from_cells())

    # Obtain parameters.
    page = request.args.get('page')
    cell_types_per_page = request.args.get('cell_types_per_page')
    starts_with = request.args.get('starts_with')
    if starts_with is None:
        starts_with = ''

    # Validate and set defaults for genes_per_page.
    if cell_types_per_page is None:
        cell_types_per_page = '10'
    if not cell_types_per_page.isnumeric():
        return make_response(f'The value for parameter cell_types_per_page ({cell_types_per_page}) '
                             f'must be numeric.', 400)
    if int(cell_types_per_page) <= 0:
        return (make_response(f'The value for parameter cell_types_per_page ({cell_types_per_page}) '
                              f'must be greater '
                              f'than zero.', 400))

    # Obtain the total count of genes, considering the filter starts_with.
    cell_type_count = celltypelist_count_get_logic(neo4j_instance, starts_with)
    if cell_type_count == 0:
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        return make_response(f"There are no cell types with preferred terms or synonyms that start "
                             f"with '{starts_with}' (case-insensitive).", 404)

    # Default values for page.
    # Case: No parameter specified.
    if page is None:
        page = '1'
    # Case: 0.
    # It is likely that a UI would supply 0 as a page parameter.
    if page == '0':
        page = '1'

    # Calculate the total number of (filtered) pages.
    total_pages = str(math.ceil(int(cell_type_count) / int(cell_types_per_page)))

    # Translation for cases "last" or "first"
    print(f'total_pages={total_pages}')
    if page == 'last':
        page = str(int(total_pages))
    if page == 'first':
        page = '1'

    # Parameter validation.
    if not page.isnumeric():
        return make_response(f"The value for parameter page ({page}) must be either a number >=0 or the words 'first' or 'last'.", 400)
    if int(page) < 0:
        return make_response(f'The value for parameter page ({page}) must be >= 0', 400)

    if int(page) > int(total_pages):
        page = str(int(total_pages))

    # Obtain results.
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(celltypelist_get_logic(neo4j_instance, page=page,
                                          total_pages=total_pages,
                                          cell_types_per_page=cell_types_per_page,
                                          starts_with=starts_with,
                                          cell_type_count=cell_type_count))
# coding: utf-8
# JAS November 2023
from flask import Blueprint, jsonify, current_app, make_response
from hs_ontology_api.utils.neo4j_logic import celltypedetail_get_logic, celltype_get_logic
# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large
from ubkg_api.utils.http_error_string import get_404_error_string

celltypes_blueprint = Blueprint('celltypes', __name__, url_prefix='/celltypes')

@celltypes_blueprint.route('/<ids>/detail', methods=['GET'])
def celltypes_id_detail_expand_get(ids=None):
    """Returns detailed information on a single cell type.

    :rtype: Union[List[CellTypeDetail]]

    """

    listids = ids.split(',')
    clids = []
    # Pad numeric ids with zeroes to 7 characters.
    for i in listids:
        if i.isnumeric():
            clids.append(f'{int(i):07d}')
        else:
            if i.strip() !='':
                clids.append(i)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = celltypedetail_get_logic(neo4j_instance, clids)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No cell types with Cell Ontology identifiers')
        return make_response(err, 404)

    # March 2025
    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)

@celltypes_blueprint.route('/<ids>', methods=['GET'])
def celltypes_id_get(ids=None):
    """
    Returns reference information on a set of cell types.
    :param ids: comma-delimited list of Cell Ontology IDs, including leading zeroes.

    """

    listids = ids.split(',')
    clids = []
    # Pad numeric ids with zeroes to 7 characters.
    for i in listids:
        if i.isnumeric():
            clids.append(f'{int(i):07d}')
        else:
            if i.strip() != '':
                clids.append(i)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = celltype_get_logic(neo4j_instance, clids)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No cell types with Cell Ontology identifiers')
        return make_response(err, 404)

    # March 2025
    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)
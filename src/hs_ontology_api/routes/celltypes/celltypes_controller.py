# coding: utf-8
# JAS November 2023
from flask import Blueprint, jsonify, current_app, make_response
from hs_ontology_api.utils.neo4j_logic import celltypedetail_get_logic
# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large
from ubkg_api.utils.http_error_string import get_404_error_string

celltypes_blueprint = Blueprint('celltypes', __name__, url_prefix='/celltypes')

@celltypes_blueprint.route('/<id>', methods=['GET'])
def celltypes_id_expand_get(id=None):
    """Returns detailed information on a single cell type.

    :rtype: Union[List[CellTypeDetail]]

    """

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = celltypedetail_get_logic(neo4j_instance, id)
    if result is None or result == []:
        # Empty result
        err = get_404_error_string(prompt_string=f'No cell types with Cell Ontology identifer')
        return make_response(err, 404)

    # March 2025
    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)
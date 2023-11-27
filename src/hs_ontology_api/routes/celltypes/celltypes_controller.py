# coding: utf-8
# JAS November 2023
from flask import Blueprint, jsonify, current_app, make_response
from hs_ontology_api.utils.neo4j_logic import celltypedetail_get_logic


celltypes_blueprint = Blueprint('celltypes', __name__, url_prefix='/celltypes')

@celltypes_blueprint.route('/<id>', methods=['GET'])
def celltypes_id_expand_get(id=None):
    """Returns detailed information on a single cell type.

    :rtype: Union[List[CellTypeDetail]]

    """

    if id =='' or id is None:
        # Missing ID parameter in URL
        return make_response('The /celltypes endpoint must specify a code from the Cell Ontology--e.g., /celltypes/0002138.',400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = celltypedetail_get_logic(neo4j_instance, id)
    if result is None or result == []:
        # Empty result
        return make_response(f"No information for cell type with Cell Ontology identifier {id}.", 404)
    return jsonify(result)
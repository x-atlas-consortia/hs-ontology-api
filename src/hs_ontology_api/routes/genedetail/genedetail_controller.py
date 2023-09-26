# coding: utf-8
# JAS September 2023
from flask import Blueprint, jsonify, current_app, request
from ..neo4j_logic import genedetail_post_logic

genedetail_blueprint = Blueprint('genes', __name__, url_prefix='/genes')

@genedetail_blueprint.route('', methods=['POST'])
def genedetail_expand_post():
    """Returns a unique list of genes.

    :rtype: Union[List[GeneDetail]]
    """
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(genedetail_post_logic(neo4j_instance, request.get_json()))
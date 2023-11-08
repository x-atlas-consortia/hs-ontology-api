from flask import Blueprint, jsonify, current_app, make_response

from hs_ontology_api.utils.neo4j_logic import relationships_for_gene_target_symbol_get_logic


relationships_blueprint = Blueprint('relationships', __name__, url_prefix='/relationships')


@relationships_blueprint.route('gene/<target_symbol>', methods=['GET'])
def relationships_for_gene_target_symbol_get(target_symbol):
    """
    Returns relationships associated with the gene target_symbol:
    Approved Symbol(s), Previous Symbols, and Alias Symbols.

    :param target_symbol: one of gene name, symbol, alias, or prior symbol
    :type target_symbol: str
    """
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = relationships_for_gene_target_symbol_get_logic(neo4j_instance, target_symbol)
    if result is None:
        resp = make_response(jsonify({"message": f"Nothing found for gene target symbol: {target_symbol}"}), 404)
        resp.headers['Content-Type'] = 'application/json'
        return resp
    return jsonify(result)

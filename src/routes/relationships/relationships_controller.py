from flask import Blueprint, jsonify, current_app, make_response


relationships_blueprint = Blueprint('relationships', __name__, url_prefix='/relationships')


@relationships_blueprint.route('gene/<target_symbol>', methods=['GET'])
def relationships_for_gene_target_symbol_get(target_symbol):
    """
    Returns relationships associated with the gene target_symbol:
    Approved Symbol(s), Previous Symbols, and Alias Symbols.

    :param target_symbol: one of gene name, symbol, alias, or prior symbol
    :type target_symbol: str
    """
    result = current_app.neo4jManager.relationships_for_gene_target_symbol_get(target_symbol)
    if result is None:
        return make_response(f"Nothing found for gene target symbol: {target_symbol}", 404)
    return jsonify(result)

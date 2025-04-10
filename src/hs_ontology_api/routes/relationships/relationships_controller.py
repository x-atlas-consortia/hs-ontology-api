from flask import Blueprint, jsonify, current_app, make_response

from hs_ontology_api.utils.neo4j_logic import relationships_for_gene_target_symbol_get_logic
# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

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
        # The use case for this endpoint is the AVR application. For possible downward compatibility issues,
        # maintain this formatting of response instead of using the get_404_error_string function from
        # the ubkg-api.
        resp = make_response(jsonify({"message": f"Nothing found for gene target symbol: {target_symbol}"}), 404)
        resp.headers['Content-Type'] = 'application/json'
        return resp

    # March 2025
    # Redirect to S3 if payload is large.
    return redirect_if_large(resp=result)

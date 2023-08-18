from flask import Blueprint, jsonify, current_app, request

from ..neo4j_logic import valueset_get_logic

valueset_blueprint = Blueprint('valueset_hs', __name__, url_prefix='/valueset')


@valueset_blueprint.route('', methods=['GET'])
def valueset_get():
    """Returns a valueset of concepts that are children (have as isa relationship) of another concept.


    :param parent_sab: the SAB of the parent concept
    :type parent_sab: str
    :param parent_code: the code of the parent concept in the SAB (local ontology)
    :type parent_code: str
    :param child_sabs: the list of SABs for child concepts, in order of preference (in case of parent concepts with cross-references)
    :type child_sabs: List[str]

    :rtype: Union[List[SabCodeTerm], Tuple[List[SabCodeTerm], int], Tuple[List[SabCodeTerm], int, Dict[str, str]]
    """
    child_sabs = request.args.getlist('child_sabs')
    if child_sabs == []:
        return jsonify("Invalid child_sabs (empty list) specified"), 400
    parent_sab = request.args.get('parent_sab')
    if parent_sab is None:
        return jsonify(f"Invalid parent_sab ({parent_sab}) specified"), 400
    parent_code = request.args.get('parent_code')
    if parent_code is None:
        return jsonify(f"Invalid parent_code ({parent_code}) specified"), 400
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(valueset_get_logic(neo4j_instance, parent_sab, parent_code, child_sabs))

from flask import Blueprint, jsonify, current_app, request

from ubkg_api.common_routes.validate import validate_application_context

from ..neo4j_logic import dataset_get_logic

datasets_blueprint = Blueprint('datasets_hs', __name__, url_prefix='/datasets')


@datasets_blueprint.route('', methods=['GET'])
def dataset_get():
    """Returns information on a set of HuBMAP or SenNet dataset types, with options to filter the list to those with specific property values. Filters are additive (i.e., boolean AND)


    :query application_context: Required filter to indicate application context.
    :type application_context: str
    :param data_type: Optional filter for data_type
    :type data_type: str
    :param description: Optional filter for display name. Use URL-encoding (space &#x3D; %20).
    :type description: str
    :param alt_name: Optional filter for a single element in the alt-names list--i.e., return datasets for which alt-names includes a value that matches the parameter. Although the field is named &#39;alt-names&#39;, the parameter uses &#39;alt_name&#39;. Use URL-encoding (space &#x3D; %20)
    :type alt_name: str
    :param primary: Optional filter to filter to primary (true) or derived (false) assay.
    :type primary: str
    :param contains_pii: Optional filter for whether the dataset contains Patient Identifying Information (PII). Although the field is named &#39;contains-pii&#39;, use &#39;contains_pii&#39; as an argument.
    :type contains_pii: str
    :param vis_only: Optional filter for whether datasets are visualization only (true). Although the field is named &#39;vis-only&#39;, use &#39;vis_only&#39; as an argument.
    :type vis_only: str
    :param vitessce_hint: Optional filter for a single element in the vitessce_hint list--i.e., return datasets for which vitessce_hints includes a value that matches the parameter. Although the field is named &#39;vitessce-hints&#39;, use &#39;vitessce_hint&#39; as an argument.
    :type vitessce_hint: str
    :param dataset_provider: Optional filter to identify the dataset provider - IEC (iec)  or external (lab)
    :type dataset_provider: str

    :rtype: Union[List[DatasetPropertyInfo], Tuple[List[DatasetPropertyInfo], int], Tuple[List[DatasetPropertyInfo], int, Dict[str, str]]
    """
    application_context = validate_application_context()
    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    return jsonify(
        dataset_get_logic(
            neo4j_instance, request.args.get('data_type'), request.args.get('description'),
            request.args.get('alt_name'), request.args.get('primary'), request.args.get('contains_pii'),
            request.args.get('vis_only'), request.args.get('vitessce_hint'), request.args.get('dataset_provider'),
            application_context)
    )

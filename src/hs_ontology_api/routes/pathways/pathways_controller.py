from flask import Blueprint, jsonify, current_app, make_response,request, abort

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum,
                                              validate_required_parameters)
from ubkg_api.utils.http_parameter import parameter_as_list

from hs_ontology_api.utils.neo4j_logic import pathway_get_logic

# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

pathways_blueprint = Blueprint('pathways_hs', __name__, url_prefix='/pathways')


@pathways_blueprint.route('/with-genes', methods=['GET'])
def pathways_with_genes_route_get():
    return pathways_with_genes_route_function_get()



def pathways_with_genes_route_function_get():
    """
    March 2025
    Returns information on the Reactome events (which can include pathways) that have
    the specified genes as participants.

    """
    # Validate parameters.
    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['geneids',
                                                              'pathwayid',
                                                              'pathwayname-startswith',
                                                              'eventtypes'])
    if err != 'ok':
        return make_response(err, 400)

    # The geneids parameter is, in general, a list of HGNC identifiers.

    geneids = parameter_as_list(param_name='geneids')
    pathwayid = request.args.get('pathwayid')
    pathwayname_startswith = request.args.get('pathwayname-startswith')

    # Check for valid event type categories.
    # The eventtypes parameter is, in general, a list.
    eventtypes = parameter_as_list(param_name='eventtypes')
    # Reactome event types, in lowercase.
    val_enum=['toplevelpathway',
              'pathway',
              'reaction',
              'blackboxevent',
              'polymerisation',
              'depolymerisation']
    if eventtypes is not None:
        for eventtype in eventtypes:
            # Normalize to the British spelling used in Reactome.
            e = eventtype.lower().replace('z','s')
            err = validate_parameter_value_in_enum(param_name='eventtypes', param_value=e, enum_list=val_enum)
            if err != 'ok':
                return make_response(err, 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = pathway_get_logic(neo4j_instance,
                               geneids=geneids,
                               pathwayid=pathwayid,
                               pathwayname_startswith=pathwayname_startswith,
                               eventtypes=eventtypes)

    iserr = result is None or result == []
    if not iserr:
        count = result.get('count')
        iserr = count == 0

    if iserr:
        # Empty result
        err = get_404_error_string(prompt_string=f"No results for "
                                                 f"specified parameters")
        return make_response(err, 404)

    return redirect_if_large(resp=result)
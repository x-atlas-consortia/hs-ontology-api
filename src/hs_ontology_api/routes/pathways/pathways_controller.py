from flask import Blueprint, jsonify, current_app, make_response,request, abort

from ubkg_api.utils.http_error_string import (get_404_error_string, validate_query_parameter_names,
                                              validate_parameter_value_in_enum,
                                              validate_required_parameters)
from ubkg_api.utils.http_parameter import parameter_as_list

from hs_ontology_api.utils.neo4j_logic import pathway_events_with_genes_get_logic, pathway_participants_get_logic

# March 2025
# S3 redirect functions
from ubkg_api.utils.s3_redirect import redirect_if_large

pathways_blueprint = Blueprint('pathways_hs', __name__, url_prefix='/pathways')


@pathways_blueprint.route('/with-genes', methods=['GET'])
def pathways_with_genes_route_get():
    return pathways_with_genes_function_get()

def pathways_with_genes_function_get():
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
    if pathwayname_startswith is not None:
        pathwayname_startswith = pathwayname_startswith.lstrip()

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
    result = pathway_events_with_genes_get_logic(neo4j_instance,
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

@pathways_blueprint.route('/<id>/participants', methods=['GET'])
def pathway_participants_route_get(id):
    return pathways_participants_function_get(id=id)

def pathways_participants_function_get(id=None):
    """
        March 2025
        Returns information on the participants in the specified Reactome event.

        :param id: an identifier of a Reactome event, which can be one of the following:
                   1. A Reactome Stable ID
                   2. The leading characters of the name of the event

        Optional filtering parameters from request arguments:
        1. sabs - list of SABs for parameters. Allowed values are:
                  a. HGNC
                  b. UNIPROTKB
                  c. CHEBI
                  d. ENSEMBL
        2. feature_types - list of ENSEMBL feature types for ENSEMBL participants.
                           Allowed values are:
                           a. gene
                           b. transcript

    """

    # Validate parameters.
    # Check for invalid parameter names.
    err = validate_query_parameter_names(parameter_name_list=['sabs','featuretypes'])
    if err != 'ok':
        return make_response(err, 400)

    id = id.lstrip()
    sabs = parameter_as_list(param_name='sabs')
    val_enum = ['HGNC',
                'UNIPROTKB',
                'ENSEMBL',
                'CHEBI']
    if sabs is not None:
        for sab in sabs:
            s = sab.upper()
            err = validate_parameter_value_in_enum(param_name='sabs', param_value=s, enum_list=val_enum)
            if err != 'ok':
                return make_response(err, 400)

    featuretypes = parameter_as_list(param_name='featuretypes')
    val_enum = ['gene','transcript']
    if featuretypes is not None:
        for feature_type in featuretypes:
            f = feature_type.lower()
            err = validate_parameter_value_in_enum(param_name='featuretypes', param_value= f,
                                                   enum_list=val_enum)
            if err != 'ok':
                return make_response(err, 400)

    neo4j_instance = current_app.neo4jConnectionHelper.instance()
    result = pathway_participants_get_logic(neo4j_instance,
                                            pathwayid=id,
                                            sabs=sabs,
                                            featuretypes=featuretypes)

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
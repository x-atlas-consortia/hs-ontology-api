import logging
import neo4j
from typing import List

from hs_ontology_api.models.assay_type_property_info import AssayTypePropertyInfo
from hs_ontology_api.models.dataset_property_info import DatasetPropertyInfo
from hs_ontology_api.models.sab_code_term_rui_code import SabCodeTermRuiCode
from hs_ontology_api.models.sab_code_term import SabCodeTerm

from ubkg_api.common_routes.common_neo4j_logic import query_cypher_dataset_info


logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def make_assaytype_property_info(record):
    return AssayTypePropertyInfo(
        record['data_type'],
        record['primary'],
        record['description'],
        record['vitessce_hints'],
        record['contains_pii'],
        record['vis_only'])


def assaytype_get_logic(neo4j_instance, primary: bool, application_context: str = 'HUBMAP')\
        -> AssayTypePropertyInfo:
    # Build the Cypher query that will return the table of data.
    query = query_cypher_dataset_info(application_context)

    assaytypes: List[dict] = []
    # Execute Cypher query and return result.
    with neo4j_instance.driver.session() as session:
        recds: neo4j.Result = session.run(query)
        for record in recds:
            if primary is None:
                assaytypes.append(make_assaytype_property_info(record).serialize())
            elif primary is True and record['primary'] is True:
                assaytypes.append(make_assaytype_property_info(record).serialize())
            elif primary is False and record['primary'] is False:
                assaytypes.append(make_assaytype_property_info(record).serialize())
    result: dict = {"result": assaytypes}
    return result


def assaytype_name_get_logic(neo4j_instance, name: str, alt_names: list = None, application_context: str = 'HUBMAP')\
        -> AssayTypePropertyInfo:
    """
    This is intended to be a drop in replacement for the same endpoint in search-src.

    The only difference is the optional application_contect to make it consistent with a HUBMAP or SENNET
    environment.
    """
    # Build the Cypher query that will return the table of data.
    query = query_cypher_dataset_info(application_context)

    # Execute Cypher query and return result.
    with neo4j_instance.driver.session() as session:
        recds: neo4j.Result = session.run(query)
        for record in recds:
            if record.get('data_type') == name and (alt_names is None or record.get('alt_names') == alt_names):
                # Accessing the record by .get('str') does not appear to work?! :-(
                return make_assaytype_property_info(record).serialize()
    return None


def dataset_get_logic(neo4j_instance, data_type: str = '', description: str = '',
                      alt_name: str = '', primary: str = '', contains_pii: str = '', vis_only: str = '',
                      vitessce_hint: str = '', dataset_provider: str = '', application_context: str = 'HUBMAP')\
        -> List[DatasetPropertyInfo]:

    # JAS FEB 2023
    # Returns an array of objects corresponding to Dataset (type) nodes in the HubMAP
    # or SenNet application ontology.
    # The return replicates the content of the original assay_types.yaml file, and adds new
    # dataset properties that were not originally in that file.

    # Arguments:
    # application_context: HUBMAP or SENNET
    # data_type...vitessce_hint: specific filtering values of properties

    # Notes:
    # 1. The order of the optional arguments must match the order of parameters in the corresponding path in the
    #    spec.yaml file.
    # 2. The field names in the response match the original keys in the original asset_types.yaml file.
    #    Unfortunately, some of these keys have names that use dashes (e.g., vis-only). Dashes are interpreted as
    #    subtraction operators in both the GET URL and in neo4j queries. This means that the parameters
    #    must use underscores instead of dashes--e.g., to filter on "vis-only", the parameter is "vis_only".

    datasets: [DatasetPropertyInfo] = []

    # Build the Cypher query that will return the table of data.
    query = query_cypher_dataset_info(application_context)

    # Execute Cypher query and return result.
    with neo4j_instance.driver.session() as session:
        recds: neo4j.Result = session.run(query)

        for record in recds:
            # Because the Cypher query concatenates a set of subqueries, filtering by a parameter
            # can only be done with the full return, except for the case of the initial subquery.

            # Filtering is additive--i.e., boolean AND.

            includerecord = True
            if data_type is not None:
                includerecord = includerecord and record.get('data_type') == data_type

            if description is not None:
                includerecord = includerecord and record.get('description') == description

            if alt_name is not None:
                includerecord = includerecord and alt_name in record.get('alt_names')

            if primary is not None:
                primarybool = primary.lower() == "true"
                includerecord = includerecord and record.get('primary') == primarybool

            if vis_only is not None:
                visbool = vis_only.lower() == "true"
                includerecord = includerecord and record.get('vis_only') == visbool

            if vitessce_hint is not None:
                includerecord = includerecord and vitessce_hint in record.get('vitessce_hints')

            if dataset_provider is not None:
                if dataset_provider.lower() == 'iec':
                    prov = application_context + ' IEC'
                else:
                    prov = 'External Provider'
                includerecord = includerecord and record.get('dataset_provider').lower() == prov.lower()

            if contains_pii is not None:
                piibool = contains_pii.lower() == "true"
                includerecord = includerecord and record.get('contains_pii') == piibool

            if includerecord:
                try:
                    dataset: [DatasetPropertyInfo] = DatasetPropertyInfo(record.get('alt_names'),
                                                                         record.get('contains_pii'),
                                                                         record.get('data_type'),
                                                                         record.get('dataset_provider'),
                                                                         record.get('description'),
                                                                         record.get('primary'),
                                                                         record.get('vis_only'),
                                                                         record.get('vitessce_hints')
                                                                         ).serialize()

                    datasets.append(dataset)
                except KeyError:
                    pass

    return datasets


def get_organ_types_logic(neo4j_instance, sab):
    """
    Objectives: Provide crosswalk information between SenNet and RUI for organ types. Replicate the original organ_types.yaml.
    1.FindSAB, code, and term for all organs.
    2.Find UBERON codes for organs.The code for Skin maps to UBERON 0002097 and UBERON 002097 cross-references
        UMLS with CUI C1123023; however, the UMLS CUI also maps to UBERON 0000014. It is necessary to specify the
        UBERON code explicitly.
    3.Find two - digit code for organs.
    Order return

    :param sab:
    :return:
    """
    result = []
    query = \
        "CALL " \
        "{ " \
        "MATCH (cParent:Code)<-[r1]-(pParent:Concept)<-[r2:isa]-(pOrgan:Concept)-[r3:CODE]->(cOrgan:Code)-[r4:PT]->(tOrgan:Term) " \
        "WHERE cParent.CodeID='SENNET C000008' " \
        f"AND r2.SAB='{sab}' " \
        f"AND cOrgan.SAB='{sab}'" \
        "AND r4.CUI=pOrgan.CUI " \
        "RETURN cOrgan.CODE as OrganCode,cOrgan.SAB as OrganSAB,tOrgan.name as OrganName, pOrgan.CUI as OrganCUI " \
        "} " \
        "CALL " \
        "{ " \
        "WITH OrganCUI " \
        "MATCH (pOrgan:Concept)-[r1:CODE]->(cOrgan:Code) " \
        "WHERE pOrgan.CUI=OrganCUI " \
        "AND cOrgan.SAB='UBERON' " \
        "RETURN DISTINCT CASE pOrgan.CUI WHEN 'C1123023' THEN 'UBERON 0002097' ELSE cOrgan.CodeID END AS OrganUBERON " \
        "} " \
        "CALL " \
        "{ " \
        "WITH OrganCUI " \
        "MATCH (pOrgan:Concept)-[r1:has_two_character_code]->(p2CC:Concept)-[r2:PREF_TERM]->(t2CC:Term) " \
        "WHERE pOrgan.CUI=OrganCUI " \
        f"AND r1.SAB='{sab}' " \
        "RETURN t2CC.name as OrganTwoCharacterCode " \
        "} " \
        "WITH OrganCode,OrganSAB,OrganName,OrganTwoCharacterCode,OrganUBERON " \
        "RETURN OrganCode,OrganSAB,OrganName,OrganUBERON,OrganTwoCharacterCode ORDER BY OrganName"

    with neo4j_instance.driver.session() as session:
        recds: neo4j.Result = session.run(query)
        for record in recds:
            item = SabCodeTermRuiCode(sab=record.get('OrganSAB'), code=record.get('OrganCode'),
                                      term=record.get('OrganName'),
                                      rui_code=record.get('OrganTwoCharacterCode'),
                                      organ_uberon=record.get('OrganUBERON')).serialize()
            result.append(item)
    return result


def relationships_for_gene_target_symbol_get_logic(neo4j_instance, target_symbol: str) -> dict:
    """
    Provide: Relationships for the gene target_symbol.

    The target_symbol can be a name, symbol, alias, or prior symbol,
    You will get this information on the matched gene if it exists:
    Approved Symbol(s), Previous Symbols, and Alias Symbols.
    You will get back 'None' if none of this information is found on the target_symbol.

    In theory there should be only one Approved Symbol, and Previous Symbol,
    but all types are returned as arrays just in case.

    Also, other relationships may exist but only those mentioned will be returned.
    """
    query: str = "CALL {" \
                 "MATCH (tSearch:Term)<-[rSearch]-(cSearch:Code)<-[:CODE]-(pSearch:Concept) " \
                 f"WHERE toUpper(tSearch.name)='{target_symbol.upper()}' AND " \
                 "cSearch.SAB='HGNC' AND " \
                 "rSearch.CUI=pSearch.CUI " \
                 "RETURN DISTINCT cSearch.CodeID AS HGNCCodeID" \
                 "} " \
                 "WITH HGNCCodeID " \
                 "MATCH (pHGNC:Concept)-[:CODE]->(cHGNC:Code)-[r]-(tHGNC:Term) " \
                 "WHERE cHGNC.CodeID=HGNCCodeID AND " \
                 "r.CUI=pHGNC.CUI AND " \
                 "type(r) IN ['ACR','NS','SYN','PT'] " \
                 "RETURN cHGNC.CODE AS code, " \
                 "CASE type(r) " \
                 "WHEN 'ACR' THEN 'symbol-approved' " \
                 "WHEN 'NS' THEN 'symbol-previous' " \
                 "WHEN 'SYN' THEN 'symbol-alias' " \
                 "WHEN 'PT' THEN 'name-approved' " \
                 "ELSE type(r) " \
                 "END AS type, " \
                 "tHGNC.name AS value " \
                 "order by type(r)"
    result: dict = {
        'symbol-approved': [],
        'symbol-previous': [],
        'symbol-alias': []
    }
    with neo4j_instance.driver.session() as session:
        recs: neo4j.Result = session.run(query)
        if recs.peek() is None:
            return None
        for rec in recs:
            try:
                type_name: str = rec['type']
                value: str = rec['value']
                if type_name == 'symbol-approved' or \
                        type_name == 'symbol-previous' or \
                        type_name == 'symbol-alias':
                    result[type_name].append(value)
            except KeyError:
                pass
    return result


def valueset_get_logic(neo4j_instance, parent_sab: str, parent_code: str, child_sabs: List[str]) -> List[SabCodeTerm]:
    # JAS 29 NOV 2022
    # Returns a valueset of concepts that are children (have as isa relationship) of another concept.

    # A valueset is defined as the set of terms associated the concept's child concepts. The parent
    # concept acts as an aggregator of concepts from multiple SABs. The main use case for a valueset
    # is an encoded set of terms that correspond to the possible answers for a categorical question.

    # The argument child_sabs is list of SABs from which to select child concepts, in order of
    # preference. If a parent concept has a cross-reference with another concept, it is likely that the
    # cross-referenced concept has child concepts from many SABs, especially if the cross-referenced concept
    # is from the UMLS. The order of SABs in the list indicates the order in which child concepts should be
    # selected.

    sabcodeterms: [SabCodeTerm] = []

    # Build clauses of the query that depend on child_sabs, including:
    # 1. an IN statement
    # 2. The CASE statement that will be used twice in the correlated subquery.
    #    The CASE statement orders the codes for child concepts by where the SABs for the child concepts
    #    occur in the child_sabs list.

    sab_case: str = 'CASE codeChild.SAB '
    sab_in: str = '['
    for index, item in enumerate(child_sabs):
        sab_case = sab_case + ' WHEN \'' + item + '\' THEN ' + str(index + 1)
        sab_in = sab_in + '\'' + item + '\''
        if index < len(child_sabs) - 1:
            sab_in = sab_in + ', '
    sab_case = sab_case + ' END'
    sab_in = sab_in + ']'

    # Build correlated subquery.

    # 1. Find the child concepts with an isa relationship with the parent HUBMAP concept (identified by code).
    # 2. Order the child concepts based on the positions of the SABs for their codes in a list
    #    (as opposed to an alphabetic order).
    # 3. Identify the code from the SAB that is the earliest in the list.  For example,
    #    if codes from SNOMEDCT_US are preferred to those from NCI, the list would include
    #    [...,'SNOMEDCT_US','NCI',...].

    query: str = 'CALL'
    query = query + '{'
    query = query + 'MATCH (codeChild:Code)<-[:CODE]-(conceptChild:Concept)-[:isa]->(conceptParent:Concept)-[' \
                    ':CODE]->(codeParent:Code) '
    query = query + ' WHERE codeParent.SAB=\'' + parent_sab + '\' AND codeParent.CODE=\'' + parent_code + '\''
    query = query + ' AND codeChild.SAB IN ' + sab_in
    query = query + ' RETURN conceptChild.CUI AS conceptChildCUI, min(' + sab_case + ') AS minSAB'
    query = query + ' ORDER BY conceptChildCUI'
    query = query + '}'

    # 4. Filter to the code for the child concepts with the "earliest" SAB. The "earliest" SAB will be different for
    #    each child concept.  Limit to 1 to account for multiple cross-references (e.g., UMLS C0026018, which maps
    #    to 2 NCI codes).
    query = query + ' CALL'
    query = query + '{'
    query = query + 'WITH conceptChildCUI, minSAB '
    query = query + 'MATCH (codeChild:Code)<-[:CODE]-(conceptChild:Concept) '
    query = query + 'WHERE conceptChild.CUI = conceptChildCUI '
    query = query + 'AND ' + sab_case + ' = minSAB '
    query = query + 'RETURN codeChild '
    query = query + 'ORDER BY codeChild.CODE '
    query = query + 'LIMIT 1'
    query = query + '} '

    # 5. Get the term associated with the child concept code with the earliest SAB.
    query = query + 'WITH codeChild,conceptChildCUI '
    query = query + 'MATCH (termChild:Term)<-[r:PT]-(codeChild:Code) '
    query = query + 'WHERE r.CUI = conceptChildCUI '
    query = query + 'RETURN termChild.name AS term, codeChild.CODE as code,codeChild.SAB as sab'

    # Execute Cypher query and return result.
    with neo4j_instance.driver.session() as session:
        recds: neo4j.Result = session.run(query)
        for record in recds:
            try:
                sabcodeterm: [SabCodeTerm] = \
                    SabCodeTerm(record.get('sab'), record.get('code'), record.get('term')).serialize()
                sabcodeterms.append(sabcodeterm)
            except KeyError:
                pass

    return sabcodeterms
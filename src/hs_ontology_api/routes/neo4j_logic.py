import logging
import neo4j
from typing import List
import pandas as pd

from flask import current_app

# Classes for JSON objects in response body
from hs_ontology_api.models.assay_type_property_info import AssayTypePropertyInfo
from hs_ontology_api.models.dataset_property_info import DatasetPropertyInfo
from hs_ontology_api.models.sab_code_term_rui_code import SabCodeTermRuiCode
from hs_ontology_api.models.sab_code_term import SabCodeTerm
# JAS Sept 2023
from hs_ontology_api.models.genedetail import GeneDetail
# JAS October 2023
from hs_ontology_api.models.genelist import GeneList
from hs_ontology_api.models.genelist_detail import GeneListDetail

# Query utilities
from hs_ontology_api.cypher.util_query import loadquerystring

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


def assaytype_get_logic(neo4j_instance, primary: bool, application_context: str = 'HUBMAP') \
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


def assaytype_name_get_logic(neo4j_instance, name: str, alt_names: list = None, application_context: str = 'HUBMAP') \
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
                      vitessce_hint: str = '', dataset_provider: str = '', application_context: str = 'HUBMAP') \
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
    # https://github.com/x-atlas-consortia/hs-ontology-api/issues/21#issuecomment-1707149316
    # first change
    #  "WHERE cParent.CodeID='SENNET C000008' " \
    # Change so that it looks like WHERE c.Parent.CodeID IN ['SAB C000008','SAB:C000008']
    # second change
    #  "RETURN DISTINCT CASE pOrgan.CUI WHEN 'C1123023' THEN 'UBERON 0002097' ELSE cOrgan.CodeID END AS OrganUBERON " \
    # Change so that the return is 'UBERON:0002097'. This will cause inconsistent results when the neo4j is in the old format, but it will not crash the return.
    #
    # https://github.com/x-atlas-consortia/ubkg-api/issues/3#issuecomment-1507273473
    # From included file 'organ_endpoint_13Apr2023.txt'...
    # //2. Find UBERON codes for organs. Special cases for duplicate cross-references:
    # //   a. The code for Skin maps to UBERON 0002097 and UBERON 002097 cross-references
    # //      UMLS with CUI C1123023; however, the UMLS CUI also maps to UBERON 0000014.
    # //   b. The code for Muscle maps to UBERON 0005090, which cross-references to UMLS C4083049, along with 2 other UBERON codes.
    # //   For these cases, it is necessary to specify the UBERON code explicitly.

    # JAS SEPT 2023
    # Deprecating the CASE statement (formerly in the second CALL block) that does manual assignments to address duplicate UBERON organ assignments.
    # "RETURN DISTINCT CASE pOrgan.CUI WHEN 'C1123023' THEN 'UBERON 0002097' WHEN 'C4083049' THEN 'UBERON 0005090'ELSE cOrgan.CodeID END AS OrganUBERON "

    # The reason for the deprecation is that the CASE statement did not truly work.
    # A UBKG ingestion can set multiple cross-references between UBERON codes and UMLS CUIs; however, the script also designates a "preferred"
    # CUI cross-reference for a code.
    # The way to pick the preferred UBERON code is to check the CUI property of the relationship
    # between the code and the preferred term (PT).

    query = \
        "CALL " \
        "{ " \
        "MATCH (cParent:Code)<-[r1]-(pParent:Concept)<-[r2:isa]-(pOrgan:Concept)-[r3:CODE]->(cOrgan:Code)-[r4:PT]->(tOrgan:Term) " \
        f"WHERE cParent.CodeID IN ['{sab} C000008','{sab}:C000008'] " \
        f"AND r2.SAB='{sab}' " \
        f"AND cOrgan.SAB='{sab}' " \
        "AND r4.CUI=pOrgan.CUI " \
        "RETURN cOrgan.CODE as OrganCode,cOrgan.SAB as OrganSAB,tOrgan.name as OrganName, pOrgan.CUI as OrganCUI " \
        "} " \
        "CALL " \
        "{ " \
        "WITH OrganCUI " \
        "MATCH (pOrgan:Concept)-[r1:CODE]->(cOrgan:Code)-[r2:PT]->(tOrgan:Term) " \
        "WHERE pOrgan.CUI=OrganCUI " \
        "AND cOrgan.SAB='UBERON' " \
        "AND r2.CUI=pOrgan.CUI " \
        "RETURN cOrgan.CodeID AS OrganUBERON" \
        "} " \
        "CALL " \
        "{ " \
        "WITH OrganCUI " \
        "MATCH (pOrgan:Concept)-[r1:has_two_character_code]->(p2CC:Concept)-[r2:PREF_TERM]->(t2CC:Term) " \
        "WHERE pOrgan.CUI=OrganCUI " \
        f"AND r1.SAB='{sab}' " \
        "RETURN t2CC.name as OrganTwoCharacterCode " \
        "} " \
        "WITH OrganCode,OrganSAB,OrganName,OrganTwoCharacterCode,OrganUBERON,OrganCUI " \
        "RETURN OrganCode,OrganSAB,OrganName,OrganUBERON,OrganTwoCharacterCode,OrganCUI ORDER BY OrganName "

    with neo4j_instance.driver.session() as session:
        recds: neo4j.Result = session.run(query)
        for record in recds:
            item = SabCodeTermRuiCode(sab=record.get('OrganSAB'), code=record.get('OrganCode'),
                                      term=record.get('OrganName'), rui_code=record.get('OrganTwoCharacterCode'),
                                      organ_uberon=record.get('OrganUBERON'), organ_cui=record.get('OrganCUI')
                                      ).serialize()
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


def __subquery_dataset_synonym_property(sab: str, cuialias: str, returnalias: str, collectvalues: bool) -> str:
    # JAS FEB 2023
    # Returns a subquery to obtain a "synonym" relationship property. See __query_dataset_info for an explanation.

    # arguments:
    # sab: SAB for the application
    # cuialias = Alias for the CUI passed to the WITH statement
    # returnalias = Alias for the return of the query
    # collectvalues: whether to use COLLECT

    qry = ''
    qry = qry + 'CALL '
    qry = qry + '{'
    qry = qry + 'WITH ' + cuialias + ' '
    qry = qry + 'OPTIONAL MATCH (pDatasetThing:Concept)-[:CODE]->(cDatasetThing:Code)-[rCodeTerm:SY]->(tSyn:Term)  '
    qry = qry + 'WHERE cDatasetThing.SAB = \'' + sab + '\''
    # In a (Concept)->(Code)->(Term) path in the KG, the relationship between the Code and Term
    # shares the CUI with the Concept.
    qry = qry + 'AND rCodeTerm.CUI = pDatasetThing.CUI '
    qry = qry + 'AND pDatasetThing.CUI = ' + cuialias + ' '
    qry = qry + 'RETURN '
    if collectvalues:
        retval = 'COLLECT(tSyn.name) '
    else:
        retval = 'tSyn.name'
    qry = qry + retval + ' AS ' + returnalias
    qry = qry + '}'

    return qry


def __subquery_dataset_relationship_property(sab: str, cuialias: str, rel_string: str, returnalias: str,
                                             isboolean: bool = False, collectvalues: bool = False,
                                             codelist: List[str] = []) -> str:
    # JAS FEB 2023
    # Returns a subquery to obtain a "relationship property". See __query_dataset_info for an explanation.

    # There are two types of relationship properties:
    # 1. The entity that associates with cuialias corresponds to the term of a related entity.
    # 2. In a "boolean" relationship, the property is true if the entity that associates with cuialias has a
    #    link of type rel_string to another code (via concepts).

    # arguments:
    # sab: SAB for the application
    # cuialias: Alias for the CUI passed to the WITH statement
    # rel_string: label for the relationship
    # returnalias:  Alias for the return of the query
    # isboolean: check for the existence of link instead of a term
    # collectvalues: whether to use COLLECT
    # codelist: list of specific codes that are objects of relationships

    qry = ''
    qry = qry + 'CALL '
    qry = qry + '{'
    qry = qry + 'WITH ' + cuialias + ' '
    qry = qry + 'OPTIONAL MATCH (pDatasetThing:Concept)-[rProperty:' + rel_string + ']->(pProperty:Concept)'

    if len(codelist) > 0:
        # Link against specific codes
        qry = qry + '-[:CODE]->(cProperty:Code)-[rCodeTerm:PT]->(tProperty:Term) '
    else:
        # Link against concepts
        qry = qry + '-[rConceptTerm:PREF_TERM]->(tProperty:Term) '

    qry = qry + 'WHERE pDatasetThing.CUI = ' + cuialias + ' '
    qry = qry + 'AND rProperty.SAB =\'' + sab + '\' '

    if len(codelist) > 0:
        # Link against specific codes.
        qry = qry + 'AND cProperty.SAB = \'' + sab + '\' '
        # In a (Concept)->(Code)->(Term) path in the KG, the relationship between the Code and Term
        # shares the CUI with the Concept.
        qry = qry + 'AND rCodeTerm.CUI = pProperty.CUI '
        qry = qry + 'AND cProperty.CODE IN [' + ','.join("'{0}'".format(x) for x in codelist) + '] '

    qry = qry + 'RETURN '
    if collectvalues:
        if rel_string == 'has_vitessce_hint':
            # Special case: some vitessce hint nodes have terms with the substring '_vitessce_hint' added.
            # This is an artifact of a requirement of the SimpleKnowledge Editor that should not be in the
            # returned result. Strip the substring.
            retval = 'COLLECT(REPLACE(tProperty.name,\'_vitessce_hint\',\'\'))'
        else:
            retval = 'COLLECT(tProperty.name) '
    elif isboolean:
        retval = 'cProperty.CodeID IS NOT NULL '
    elif 'C004003' in codelist:
        # Special case: map dataset orders to true or false
        retval = 'CASE cProperty.CODE WHEN \'C004003\' THEN true WHEN \'C004004\' THEN false ELSE \'\' END '
    else:
        # Force a blank in case of null value for a consistent return to the GET.
        retval = 'CASE tProperty.name WHEN NULL THEN \'\' ELSE tProperty.name END '

    qry = qry + retval + ' AS ' + returnalias
    qry = qry + '}'
    return qry


def __subquery_data_type_info(sab: str) -> str:
    # JAS FEB 2023
    # Returns a Cypher subquery that obtains concept CUI and preferred term strings for the Dataset Data Type
    # codes in an application context. Dataset Data Type codes are in a hierarchy with a root entity with code
    # C004001 in the application context.

    # See __build_cypher_dataset_info for an explanation.

    # Arguments:
    # sab: the SAB for the application ontology context--i.e., either HUBMAP or SENNET filter: filter for data_type

    qry = ''
    qry = qry + 'CALL '
    qry = qry + '{'
    qry = qry + 'MATCH (cParent:Code)<-[:CODE]-(pParent:Concept)<-[:isa]-(pChild:Concept)'
    qry = qry + '-[rConceptTerm:PREF_TERM]->(tChild:Term) '
    # https://github.com/x-atlas-consortia/hs-ontology-api/issues/21#issuecomment-1707149316
    # qry = qry + 'WHERE cParent.CodeID=\'' + sab + ' C004001\' '
    # Change so that it looks like WHERE c.Parent.CodeID IN ['SAB C004001','SAB:C004001']
    qry = qry + f"WHERE cParent.CodeID IN ['{sab} C004001','{sab}:C004001'] "
    qry = qry + 'RETURN pChild.CUI AS data_typeCUI, tChild.name AS data_type'
    qry = qry + '} '
    return qry


def __subquery_dataset_cuis(sab: str, cuialias: str, returnalias: str) -> str:
    # JAS FEB 2023
    # Returns a Cypher subquery that obtains concept CUIs for Dataset concepts in the application context.
    # The use case is that the concepts are related to the data_set CUIs passed in the cuialias parameter.

    # arguments:
    # sab: SAB for the application
    # cuialias: CUI to pass to the WITH statement
    # returnalias: alias for return

    qry = ''
    qry = qry + 'CALL '
    qry = qry + '{'
    qry = qry + 'WITH ' + cuialias + ' '
    qry = qry + 'OPTIONAL MATCH (pDataType:Concept)<-[r:has_data_type]-(pDataset:Concept)  '
    qry = qry + 'WHERE r.SAB =\'' + sab + '\' '
    qry = qry + 'AND pDataType.CUI = ' + cuialias + ' '
    qry = qry + 'RETURN pDataset.CUI AS ' + returnalias
    qry = qry + '}'

    return qry


def query_cypher_dataset_info(sab: str) -> str:
    # JAS FEB 2023
    # Returns a Cypher query string that will return property information on the datasets in an application
    # context (SAB in the KG), keyed by the data_type.

    # Arguments:
    # sab: the SAB for the application ontology context--i.e., either HUBMAP or SENNET

    # There are three types of "properties" for an entity in an ontology (i.e., those specified by assertion
    # in the SAB, and not lower-level infrastructural properties such as SAB or CUI):
    # 1. A "relationship property" corresponds to the name property of the Term node in a path that corresponds
    #    to an asserted relationship other than isa--i.e.,
    #    (Term)<-[:PT]-(Code)<-[:CODE]-(Concept)-[property relationship]-(Concept)-[:CODE]-(Code for Entity)
    # 2. A "hierarchy property" corresponds to a "relationship property" of a node to which the entity relates
    #    by means of an isa relationship.
    #    For example, the Dataset Order property (Primary Dataset, Derived Dataset) is actually a property of a
    #    subclass of Dataset Order to which Dataset relates via an isa relationship. If a Dataset isa
    #    Primary Dataset, then it has a "Dataset order" property of "Primary Dataset".
    # 3. A "synonym property", in which the property value corresponds to the name of a Term node that has a
    #    SY relationship with the Code node for the entity.

    # In an application ontology, dataset properties can associate with the dataset or the data_type.

    # The data_type is actually a property of a Dataset type  (relationship = has_data_type).
    # Instead of navigating from the Dataset types down to properties, the query will navigate from
    # the data_types up to the Dataset types and then down to the other dataset properties.

    # The original assay_types.yaml file has keys that use dashes instead of underscores--e.g., alt-names.
    # neo4j cannot interpret return variables that contain dashes, so the query string uses underscores--
    # e.g., alt_names. The ubkg-src-spec.yaml file uses dashes for key names for the return to the GET.

    sab = sab.upper()

    qry = ''

    # First, identify the CUIs and terms for data_type in the specified application.
    # The subquery will return:
    # data_typeCUI - used in the WITH clause of downstream subqueries for properties that link to the data_type.
    # data_type - used in the return
    qry = qry + __subquery_data_type_info(sab=sab)

    # Identify CUIs for dataset types that associate with the data_type.
    # The subquery will return DatasetCUI, used in the WITH clause of downstream subqueries that link to the
    # Dataset.
    qry = qry + ' ' + __subquery_dataset_cuis(sab=sab, cuialias='data_typeCUI', returnalias='DatasetCUI')

    # PROPERTY VALUE SUBQUERIES

    # Dataset display name: relationship property of the Dataset.
    qry = qry + ' ' + __subquery_dataset_relationship_property(sab=sab, cuialias='DatasetCUI',
                                                               rel_string='has_display_name',
                                                               returnalias='description')

    # alt_names: Synonym property, linked to the data_type.
    # Because a data_type can have multiple alt-names, collect values.
    qry = qry + ' ' + __subquery_dataset_synonym_property(sab=sab, cuialias='data_typeCUI', returnalias='alt_names',
                                                          collectvalues=True)

    # dataset_order: relationship property, linked to Dataset.
    # C004003=Primary Dataset, C004004=Derived Dataset in both HuBMAP and SenNet.
    qry = qry + ' ' + __subquery_dataset_relationship_property(sab=sab, cuialias='DatasetCUI', rel_string='isa',
                                                               returnalias='primary', codelist=['C004003', 'C004004'])

    # dataset_provider: relationship property of the Dataset.
    qry = qry + ' ' + __subquery_dataset_relationship_property(sab=sab, cuialias='DatasetCUI',
                                                               rel_string='provided_by',
                                                               returnalias='dataset_provider')

    # vis-only: "boolean" relationship property of the Dataset.
    # True = the Dataset isa <SAB> C004008 (vis-only).
    qry = qry + ' ' + __subquery_dataset_relationship_property(sab=sab, cuialias='DatasetCUI', rel_string='isa',
                                                               returnalias='vis_only', isboolean=True,
                                                               codelist=['C004008'])

    # contains_pii: "boolean" relationship property of the Dataset.
    # True = the Dataset has a path to code <SAB> C004009 (pii).
    qry = qry + ' ' + __subquery_dataset_relationship_property(sab=sab, cuialias='DatasetCUI',
                                                               returnalias='contains_pii', rel_string='contains',
                                                               isboolean=True, codelist=['C004009'])

    # vitessce_hints: list relationship property of the data_type.
    qry = qry + ' ' + __subquery_dataset_relationship_property(sab=sab, cuialias='data_typeCUI',
                                                               rel_string='has_vitessce_hint',
                                                               returnalias='vitessce_hints', collectvalues=True)

    # Order and sort output
    qry = qry + ' '
    qry = qry + 'WITH data_type, description, alt_names, primary, dataset_provider, vis_only, contains_pii, vitessce_hints '
    qry = qry + 'RETURN data_type, description, alt_names, primary, dataset_provider, vis_only, contains_pii, vitessce_hints '
    qry = qry + 'ORDER BY tolower(data_type)'
    return qry

def genedetail_get_logic(neo4j_instance, gene_id: str) -> List[GeneDetail]:
    """
    Returns detailed information on a gene, based on an input list of HGNC identifiers in the request body of a POST.
    """
    # response list

    # Read indexed cell-type data from Cells API.
    # The cells_client was instantiated at startup.
    oc = current_app.cells_client

    # The current prototype call reads a CSV of static information obtained from
    # prior calls to the Cells API.
    cellsapi_celltypes = oc.celltypes_for_gene_csv(gene_id)
    genedetails: [GeneDetail] = []

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'genedetail.cypher'
    query = loadquerystring(queryfile)

    query = query.replace('$ids', f'\'{gene_id}\'')

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        # Build response object.
        for record in recds:
            try:
                genedetail: GeneDetail = \
                    GeneDetail(record.get('hgnc_id'), record.get('approved_symbol'), record.get('approved_name'),
                               record.get('previous_symbols'), record.get('previous_names'),
                               record.get('alias_symbols'),
                               record.get('alias_names'), record.get('references'), record.get('summaries'),
                               record.get('cell_types_code'), record.get('cell_types_code_name'),
                               record.get('cell_types_code_definition'),
                               record.get('cell_types_codes_organ'),record.get('cell_types_codes_source')).serialize()

                # Append cell type information from Cells API.
                for cell_type in cellsapi_celltypes:
                    genedetail['cell_types'].append(cell_type)
                genedetails.append(genedetail)

            except KeyError:
                pass

    return genedetails

def genelist_get_logic(neo4j_instance, page:str, total_pages:str, genesperpage:str, starts_with:str) -> List[GeneList]:

    """
    Returns information on HGNC genes.
    Intended to support a Data Portal landing page featuring a high-level
    list with pagination features.

    :param neo4j_instance:  neo4j client
    :page: Zero-based number of pages with rows=pagesize to skip in neo4j query
    :genesperpage: number of rows to limit in neo4j query
    :return: List[GeneList]
    :startswith: string for type-ahead (starts with) searches
    :return: str

    """

    # response list
    retlist: [GeneList] = []

    # Load annotated Cypher query from the cypher directory.
    queryfile = 'geneslist.cypher'
    query = loadquerystring(queryfile)

    # The query is parameterized with variables $skiprows and $limitrows.
    # Calculate variable values from parameters.

    # SKIP in the neo4j query is 0-based--i.e., SKIP 0 means the first page.
    # UI-based pagination, however, is 1-based.
    # The controller will pass a default value of 1 for cases of no value (default)
    # or 0.
    # Convert to 1-based.
    intpage = int(page)-1

    skiprows = intpage * int(genesperpage)

    starts_with_clause = ''
    if starts_with != '':
        starts_with_clause = f'AND map[\'approved_symbol\'][0] STARTS WITH \'{starts_with}\''
    query = query.replace('$starts_with_clause',starts_with_clause)
    query = query.replace('$skiprows', str(skiprows))
    query = query.replace('$limitrows', str(genesperpage))

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        genes: [GeneListDetail] = []
        # Build the list of gene details for this page.
        for record in recds:
            try:
                gene: GeneListDetail = \
                    GeneListDetail(record.get('hgnc_id'), record.get('approved_symbol'), record.get('approved_name'), record.get('description')).serialize()
                genes.append(gene)
            except KeyError:
                pass
        # Use the list of gene details with the page to build a genelist object.
        genelist: GeneList = GeneList(page, total_pages, genesperpage, genes, starts_with).serialize()
    return genelist

def genelist_count_get_logic(neo4j_instance) -> int:

    # Returns the count of HGNC genes in the UBKG.

    # Load annotated Cypher query from the cypher directory.
    queryfile = 'geneslist_count.cypher'
    query = loadquerystring(queryfile)
    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        for record in recds:
            try:
                genecount = record.get('genelistcount')
            except KeyError:
                pass
    return genecount


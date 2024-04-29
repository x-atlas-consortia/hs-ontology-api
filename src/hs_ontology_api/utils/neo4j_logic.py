import logging
import neo4j
from typing import List
# import pandas as pd
import os

# from flask import current_app

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
# JAS Nov 2023
from hs_ontology_api.models.proteinlist_detail import ProteinListDetail
from hs_ontology_api.models.proteinlist import ProteinList
from hs_ontology_api.models.proteindetail import ProteinDetail
from hs_ontology_api.models.celltypelist import CelltypeList
from hs_ontology_api.models.celltypelist_detail import CelltypesListDetail
from hs_ontology_api.models.celltypedetail import CelltypeDetail
# JAS Dec 2023
from hs_ontology_api.models.fielddescription import FieldDescription
from hs_ontology_api.models.fieldtype import FieldType
from hs_ontology_api.models.fieldassay import FieldAssay
# JAS Jan 2024
from hs_ontology_api.models.fieldschema import FieldSchema
from hs_ontology_api.models.fieldtype_detail import FieldTypeDetail
from hs_ontology_api.models.fieldentity import FieldEntity
# custom exception classes
from .hsontologyexception import DuplicateFieldError

# Query utilities
# from hs_ontology_api.cypher.util_query import loadquerystring

logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def loadquerystring(filename: str) -> str:

    # Load a query string from a file.
    # filename: filename, without path.

    # Assumes that the file is in the cypher directory.

    fpath = os.path.dirname(os.getcwd())
    fpath = os.path.join(fpath, 'src/hs_ontology_api/cypher', filename)

    f = open(fpath, "r")
    query = f.read()
    f.close()
    return query


def make_assaytype_property_info(record):

    # JAS 11 December 2023 Although the class AssayTypePropertyInfo uses underscores for
    # properties such as contains_pii, the serialization converts the underscores to dashes.

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
    Objectives: Provide crosswalk information between organs and RUI.
    Replicates the call  original organ_types.yaml.

    :param sab: SAB for application context
    :param neo4j_instance: pointer to neo4j connection
    :return:

    JAS NOV 2023 - Moved query string to external file and implemented loadquery utility logic.
    """
    result = []

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $sab.
    queryfile = 'organs.cypher'
    query = loadquerystring(queryfile)
    query = query.replace('$sab', f'\'{sab}\'')

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
    # JAS Nov 2023 limit SABs for isa relationship to specified child values
    query = query + 'MATCH (codeChild:Code)<-[:CODE]-(conceptChild:Concept)-[r:isa]->(conceptParent:Concept)-[' \
                    ':CODE]->(codeParent:Code) '
    query = query + ' WHERE codeParent.SAB=\'' + parent_sab + '\' AND codeParent.CODE=\'' + parent_code + '\''
    query = query + ' AND codeChild.SAB IN ' + sab_in
    # JAS Nov 2023 limit SABs for isa relationship to specified child values
    query = query + ' AND r.SAB IN ' + sab_in
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
    Returns detailed information on a gene, based on an HGNC identifer.
    :param neo4j_instance: instance of neo4j connection
    :param gene_id: HGNC identifier for a gene
    """
    # response list
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
                    GeneDetail(hgnc_id=record.get('hgnc_id'),
                               approved_symbol=record.get('approved_symbol'),
                               approved_name=record.get('approved_name'),
                               previous_symbols=record.get('previous_symbols'),
                               previous_names=record.get('previous_names'),
                               alias_symbols=record.get('alias_symbols'),
                               alias_names=record.get('alias_names'),
                               references=record.get('references'),
                               summaries=record.get('summaries'),
                               cell_types_code=record.get('cell_types_code'),
                               cell_types_code_name=record.get('cell_types_code_name'),
                               cell_types_code_definition=record.get('cell_types_code_definition'),
                               cell_types_codes_organ=record.get('cell_types_codes_organ'),
                               cell_types_code_source=record.get('cell_types_codes_source')).serialize()

                genedetails.append(genedetail)

            except KeyError:
                pass

    return genedetails


def genelist_count_get_logic(neo4j_instance, starts_with: str) -> int:
    """
        Returns the count of HGNC genes in the UBKG.
        If starts_with is non-null, returns the count of HGNC genes with approved symbol
        that starts with the parameter value.
        :param neo4j_instance:  neo4j client
        :param starts_with: filtering string for STARTS WITH queries
        :return: integer count
    """
    #

    # Load annotated Cypher query from the cypher directory.
    queryfile = 'geneslist_count.cypher'
    query = loadquerystring(queryfile)
    starts_with_clause = ''
    if starts_with != '':
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f'AND tGene.name STARTS WITH "{starts_with}"'
    query = query.replace('$starts_with_clause', starts_with_clause)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        for record in recds:
            try:
                gene_count = record.get('genelistcount')
            except KeyError:
                pass
    return gene_count


def genelist_get_logic(neo4j_instance, page: str, total_pages: str, genes_per_page: str, starts_with: str,
                       gene_count: str) -> List[GeneList]:

    """
    Returns information on HGNC genes.
    Intended to support a Data Portal landing page featuring a high-level
    list with pagination features.

    :param neo4j_instance:  neo4j client
    :param page: Zero-based number of pages with rows=pagesize to skip in neo4j query
    :param total_pages: Calculated number of pages of genes
    :param genes_per_page: number of rows to limit in neo4j query
    :param starts_with: string for type-ahead (starts with) searches
    :param gene_count: Calculated total count of genes, optionally filtered with starts_with
    :return: List[GeneList]

    """

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

    skiprows = intpage * int(genes_per_page)

    starts_with_clause = ''
    if starts_with != '':
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f'AND map["approved_symbol"][0] STARTS WITH "{starts_with}"'
    query = query.replace('$starts_with_clause', starts_with_clause)
    query = query.replace('$skiprows', str(skiprows))
    query = query.replace('$limitrows', str(genes_per_page))

    print(query)
    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        genes: [GeneListDetail] = []
        # Build the list of gene details for this page.
        for record in recds:
            try:
                gene: GeneListDetail = \
                    GeneListDetail(hgnc_id=record.get('hgnc_id'),
                                   approved_symbol=record.get('approved_symbol'),
                                   approved_name=record.get('approved_name'),
                                   summary=record.get('description')).serialize()
                genes.append(gene)
            except KeyError:
                pass
        # Use the list of gene details with the page to build a genelist object.
        genelist: GeneList = GeneList(page=page, total_pages=total_pages, genes_per_page=genes_per_page, genes=genes,
                                      starts_with=starts_with, gene_count=gene_count).serialize()
    return genelist


def proteinlist_get_logic(neo4j_instance, page: str, total_pages: str, proteins_per_page: str, starts_with: str,
                          protein_count: str) -> List[GeneList]:

    """
    Returns information on UNIPROTKB proteins.
    Intended to support a Data Portal landing page featuring a high-level
    list with pagination features.

    :param neo4j_instance:  neo4j client
    :param page: Zero-based number of pages with rows=pagesize to skip in neo4j query
    :param total_pages: Calculated number of pages of genes
    :param proteins_per_page: number of rows to limit in neo4j query
    :param starts_with: string for type-ahead (starts with) searches
    :param protein_count: Calculated total count of genes, optionally filtered with starts_with
    :return: List[ProteinList]

    """

    # Load annotated Cypher query from the cypher directory.
    queryfile = 'proteinslist.cypher'
    query = loadquerystring(queryfile)

    # The query is parameterized with variables $skiprows and $limitrows.
    # Calculate variable values from parameters.

    # SKIP in the neo4j query is 0-based--i.e., SKIP 0 means the first page.
    # UI-based pagination, however, is 1-based.
    # The controller will pass a default value of 1 for cases of no value (default)
    # or 0.
    # Convert to 1-based.
    intpage = int(page)-1

    skiprows = intpage * int(proteins_per_page)

    starts_with_clause = ''
    if starts_with != '':
        # Symbols will not be available until the UNIPROTKB ETL bug with synonyms with parentheses is fixed.
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f' AND (toLower(id) STARTS WITH "{starts_with.lower()}" ' \
                             f' OR toLower(map["entry_name"][0]) STARTS WITH "{starts_with.lower()}" ' \
                             f' OR toLower(map["recommended_name"][0]) STARTS WITH "{starts_with.lower()}" )' # \
                             # f'OR ANY (n in map[\'synonyms\'] WHERE n.name STARTS WITH \'{starts_with}\')'
    query = query.replace('$starts_with_clause', starts_with_clause)
    query = query.replace('$skiprows', str(skiprows))
    query = query.replace('$limitrows', str(proteins_per_page))

    if starts_with != '':
        starts_with = f'{starts_with} (case-insensitive)'

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        proteins: [ProteinListDetail] = []
        # Build the list of gene details for this page.
        for record in recds:
            try:
                protein: ProteinListDetail = \
                    ProteinListDetail(uniprotkb_id=record.get('id'), recommended_name=record.get('recommended_name'),
                                      entry_name=record.get('entry_name'), synonyms=record.get('synonyms')).serialize()
                proteins.append(protein)
            except KeyError:
                pass
        # Use the list of protein details with the page to build a ProteinList object.
        proteinlist: ProteinList = ProteinList(page=page, total_pages=total_pages, proteins_per_page=proteins_per_page,
                                               proteins=proteins, starts_with=starts_with,
                                               protein_count=protein_count).serialize()
    return proteinlist


def proteinlist_count_get_logic(neo4j_instance, starts_with: str) -> int:
    """
        Returns the count of UniProtKB proteins in the UBKG.
        If starts_with is non-null, returns the count of UniProtKB proteins with identifier
        (approved name, entry name, or synonym) that starts with the parameter value.
        :param neo4j_instance:  neo4j client
        :param starts_with: filtering string for STARTS WITH queries
        :return: integer count
    """
    #

    # Load annotated Cypher query from the cypher directory.
    queryfile = 'proteinslist_count.cypher'
    query = loadquerystring(queryfile)
    starts_with_clause = ''
    if starts_with != '':
        # Check for recommended_name, entry_name, or one of the list of symbols.
        # (Symbols will not be available until the UNIPROTKB ETL bug with synonyms with parentheses is fixed.)
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f' AND (toLower(id) STARTS WITH "{starts_with.lower()}" ' \
                             f' OR toLower(map["entry_name"][0]) STARTS WITH "{starts_with.lower()}" ' \
                             f' OR toLower(map["recommended_name"][0]) STARTS WITH "{starts_with.lower()}") ' # \
                             # f'OR ANY (n in map[\'synonyms\'] WHERE n.name STARTS WITH \'{starts_with}\')'

    query = query.replace('$starts_with_clause', starts_with_clause)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        for record in recds:
            try:
                protein_count = record.get('proteinlistcount')
            except KeyError:
                pass
    return protein_count


def proteindetail_get_logic(neo4j_instance, protein_id: str) -> List[ProteinDetail]:
    """
    Returns detailed information on a protein, based a UniProtKB identifier.
    :param neo4j_instance: instance of neo4j connection
    :param protein_id: UniProtKB identifier for a protein--either a UniProtKB ID or entry name
    """
    # response list
    proteindetails: [ProteinDetail] = []

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'proteindetail.cypher'
    query = loadquerystring(queryfile)

    query = query.replace('$ids', f'\'{protein_id}\'')

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        # Build response object.
        for record in recds:
            try:
                proteindetail: ProteinDetail = \
                    ProteinDetail(uniprotkb_id=record.get('id'), recommended_name=record.get('recommended_name'),
                                  entry_name=record.get('entry_name'), synonyms=record.get('synonyms'),
                                  description=record.get('description')).serialize()

                proteindetails.append(proteindetail)

            except KeyError:
                pass

    return proteindetails


def celltypelist_count_get_logic(neo4j_instance, starts_with: str) -> int:
    """
        Returns the count of Cell Ontology codes in the UBKG.
        If starts_with is non-null, returns the count of UniProtKB proteins with case-insensitive identifier
        (preferred term or synonym) that starts with the parameter value.
        :param neo4j_instance:  neo4j client
        :param starts_with: filtering string for STARTS WITH queries
        :return: integer count
    """
    #

    # Load annotated Cypher query from the cypher directory.
    queryfile = 'celltypeslist_count.cypher'
    query = loadquerystring(queryfile)
    starts_with_clause = ''
    if starts_with != '':
        # Check for preferred term or synonym.
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f' AND toLower(t.name) STARTS WITH "{starts_with.lower()}"' \

    query = query.replace('$starts_with_clause', starts_with_clause)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        for record in recds:
            try:
                celltype_count = record.get('celltypelistcount')
            except KeyError:
                pass

    return celltype_count


def celltypelist_get_logic(neo4j_instance, page: str, total_pages: str, cell_types_per_page: str,
                           starts_with: str, cell_type_count: str) -> List[CelltypeList]:

    """
    Returns information on HGNC genes.
    Intended to support a Data Portal landing page featuring a high-level
    list with pagination features.

    :param neo4j_instance:  neo4j client
    :param page: Zero-based number of pages with rows=pagesize to skip in neo4j query
    :param total_pages: Calculated number of pages of cell types
    :param cell_types_per_page: number of rows to limit in neo4j query
    :param starts_with: string for type-ahead (starts with) searches
    :param cell_type_count: Calculated total count of cell types, optionally filtered with starts_with
    :return: List[CelltypeList]

    """

    # Load annotated Cypher query from the cypher directory.
    queryfile = 'celltypeslist.cypher'
    query = loadquerystring(queryfile)

    # The query is parameterized with variables $skiprows and $limitrows.
    # Calculate variable values from parameters.

    # SKIP in the neo4j query is 0-based--i.e., SKIP 0 means the first page.
    # UI-based pagination, however, is 1-based.
    # The controller will pass a default value of 1 for cases of no value (default)
    # or 0.
    # Convert to 1-based.
    intpage = int(page)-1

    skiprows = intpage * int(cell_types_per_page)

    starts_with_clause = ''
    if starts_with != '':
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f' AND toLower(t.name) STARTS WITH "{starts_with.lower()}"' \

    query = query.replace('$starts_with_clause', starts_with_clause)
    query = query.replace('$skiprows', str(skiprows))
    query = query.replace('$limitrows', str(cell_types_per_page))

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        cell_types: [CelltypesListDetail] = []
        # Build the list of gene details for this page.
        for record in recds:
            try:
                cell_type: CelltypesListDetail = \
                    CelltypesListDetail(id=record.get('id'),
                                        term=record.get('term'),
                                        synonyms=record.get('synonyms'),
                                        definition=record.get('definition')).serialize()
                cell_types.append(cell_type)
            except KeyError:
                pass
        # Use the list of gene details with the page to build a genelist object.
        celltypelist: CelltypeList = CelltypeList(page=page,
                                                  total_pages=total_pages,
                                                  cell_types_per_page=cell_types_per_page,
                                                  cell_types=cell_types,
                                                  starts_with=starts_with,
                                                  cell_type_count=cell_type_count).serialize()
    return celltypelist


def celltypedetail_get_logic(neo4j_instance, cl_id: str) -> List[GeneDetail]:
    """
    Returns detailed information on a cell type, based on a Cell Ontology ID.
    :param neo4j_instance: instance of neo4j connection
    :param cl_id: Cell Ontology identifier
    """
    # response list
    celltypedetails: [GeneDetail] = []

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'celltypedetail.cypher'
    query = loadquerystring(queryfile)

    query = query.replace('$ids', f'\'{cl_id}\'')

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        # Build response object.
        for record in recds:
            try:
                celltypedetail: CelltypeDetail = \
                    CelltypeDetail(cl_id=record.get('CLID'),
                                   name=record.get('cell_types_code_name'),
                                   definition=record.get('cell_types_definition'),
                                   biomarkers=record.get('cell_types_genes'),
                                   organs=record.get('cell_types_organs')).serialize()

                celltypedetails.append(celltypedetail)

            except KeyError:
                pass

    return celltypedetails


def field_descriptions_get_logic(neo4j_instance, field_name=None, definition_source=None) -> List[FieldDescription]:
    """
    Returns detailed information on an ingest metadata field description.
    :param: neo4j_instance - neo4j connection
    :param: field_name - field name (for field-description/{name} route)
    :param: definition_source - source of field description-- HMFIELD or CEDAR
    """
    # response list
    fielddescriptions: [FieldDescription] = []

    # Used in WHERE clauses when no filter is needed.
    identity_filter = '1=1'

    # Load annotated Cypher query from the cypher directory.

    queryfile = 'fielddescriptions.cypher'
    query = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    query = query.replace('$field_filter', field_filter)

    # Allow for filtering on description source
    if definition_source is None:
        source_filter = " AND d.SAB IN ['HMFIELD', 'CEDAR'] "
    elif definition_source in ['HMFIELD', 'CEDAR']:
        source_filter = f" AND d.SAB = '{definition_source}'"
    else:
        source_filter = " AND d.SAB IN ['HMFIELD', 'CEDAR'] "

    query = query.replace('$source_filter', source_filter)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        record_count = 0
        # Build response object.
        for record in recds:
            try:
                fielddescription: FieldDescription = \
                    FieldDescription(code_ids=record.get('code_ids'),
                                     name=record.get('identifier'),
                                     descriptions=record.get('defs')).serialize()

                fielddescriptions.append(fielddescription)
                record_count = record_count + 1
            except KeyError:
                pass

    return fielddescriptions

def field_types_get_logic(neo4j_instance, field_name=None, mapping_source=None, type_source=None, type=None)\
        -> List[FieldType]:
    """
    Returns detailed information on an ingest metadata field's associated data types.
    The types here are not to be confused
    with the dataset data type--e.g., they are values like "string", "integer", etc.

    :param neo4j_instance: neo4j connection
    :param field_name: name of the metadata field
    :param mapping_source: name of the source of field-type mapping--i.e., HMFIELD or CEDAR
    :param type_source: name of the source of the field term--i.e., the type ontology. Choices are HMFIELD and XSD.
    :param type: term for the type--e.g., string
    """
    # response list
    fieldtypes: [FieldType] = []

    # Used in WHERE clauses when no filter is needed.
    identity_filter = '1=1'

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'fieldtypes.cypher'
    query = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    query = query.replace('$field_filter', field_filter)

    # Allow for filtering on mapping source.
    if mapping_source is None:
        mapping_source_filter = " AND rdt.SAB IN ['HMFIELD', 'CEDAR'] "
    elif mapping_source in ['HMFIELD', 'CEDAR']:
        mapping_source_filter = f" AND rdt.SAB = '{mapping_source}'"
    else:
        mapping_source_filter = " AND rdt.SAB IN ['HMFIELD', 'CEDAR'] "
    query = query.replace('$mapping_source_filter', mapping_source_filter)

    # Allow for filtering on type source.
    if type_source is None:
        type_source_filter = " AND cType.SAB IN ['HMFIELD', 'XSD'] "
    elif type_source in ['HMFIELD', 'XSD']:
        type_source_filter = f" AND cType.SAB = '{type_source}'"
    else:
        type_source_filter = " AND cType.SAB IN ['HMFIELD', 'XSD'] "
    query = query.replace('$type_source_filter', type_source_filter)

    # Allow for filtering on type.
    if type is None:
        type_filter = f"AND {identity_filter}"
    else:
        type_filter = f"AND CASE WHEN tType.name CONTAINS ':' THEN split(tType.name,':')[1] " \
                      f"ELSE tType.name END='{type}'"
    query = query.replace('$type_filter', type_filter)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        record_count = 0
        # Build response object.
        for record in recds:
            try:
                fieldtype: FieldType = \
                    FieldType(code_ids=record.get('code_ids'),
                              name=record.get('field_name'),
                              types=record.get('types')).serialize()

                fieldtypes.append(fieldtype)
                record_count = record_count + 1
            except KeyError:
                pass

    return fieldtypes

def field_types_info_get_logic(neo4j_instance, type_source=None):
    """
    Returns a unique list of available field data types, with optional filtering.
    Used by the field-types-info endpoint.

    :param neo4j_instance: neo4j connection
    :param type_source:  name of the source of the field term--i.e., the type ontology. Choices are HMFIELD and XSD.
    :return:
    """
    # response list
    fieldtypes: [FieldTypeDetail] = []

    # Used in WHERE clauses when no filter is needed.
    identity_filter = '1=1'

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'fieldtypelist.cypher'
    query = loadquerystring(queryfile)

    # Allow for filtering on type source.
    if type_source is None:
        type_source_filter = " AND cType.SAB IN ['HMFIELD', 'XSD'] "
    elif type_source in ['HMFIELD', 'XSD']:
        type_source_filter = f" AND cType.SAB = '{type_source}'"
    else:
        type_source_filter = " AND cType.SAB IN ['HMFIELD', 'XSD'] "
    query = query.replace('$type_source_filter', type_source_filter)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        # Build response object.
        for record in recds:
            try:
                fieldtypedetail: FieldTypeDetail = \
                    FieldTypeDetail(type_detail=record.get('type'), is_mapped=False).serialize()

                fieldtypes.append(fieldtypedetail)

            except KeyError:
                pass

    return fieldtypes


def field_assays_get_logic(neo4j_instance, field_name=None, assay_identifier=None,
                           data_type=None, dataset_type=None) -> List[FieldAssay]:
    """
    Returns detailed information on the associations between a  metadata field and assay datasets.
    :param neo4j_instance: connection to UBKG instance
    :param field_name: optional filter: name of field
    :param assay_identifier: optional filter: name of assay_identifier used in legacy field_assays.yaml.
    This corresponds to a data_type; an alt-name, or a description.
    :param data_type: legacy data_type
    :param dataset_type: soft assay dataset type
    :return:
    """

    # response list
    fieldassays: [FieldAssay] = []

    # Used in WHERE clauses when no filter is needed.
    identity_filter = '1=1'

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'fieldassays.cypher'
    query = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    query = query.replace('$field_filter', field_filter)

    # Allow for filtering on assay_identifier.
    if assay_identifier is None:
        assay_type_filter = f'AND {identity_filter}'
    else:
        assay_type_filter = f" AND tAssay.name='{assay_identifier}'"

    query = query.replace('$assay_type_filter', assay_type_filter)

    # Allow for filtering on data_type and dataset_type
    list_data_filters = []
    if data_type is None:
        list_data_filters.append(identity_filter)
    else:
        list_data_filters.append(f"data_type='{data_type}'")

    if dataset_type is None:
        list_data_filters.append(identity_filter)
    else:
        list_data_filters.append(f"dataset_type='{dataset_type}'")

    if len(list_data_filters) == 0:
        filter = f' WHERE {identity_filter}'
    else:
        filter = ' WHERE ' + ' AND '.join(list_data_filters)

    query = query.replace('$data_type_dataset_type_filters', filter)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        record_count = 0

        # Build response object. Valid responses contain something in the assays element other than
        # ['none|none|none'].
        for record in recds:
            try:
                if record.get('assays') != ['none|none|none']:
                    fieldassay: FieldAssay = \
                        FieldAssay(code_ids=record.get('code_ids'),
                                   name=record.get('field_name'),
                                   assays=record.get('assays')).serialize()
                    fieldassays.append(fieldassay)
                    record_count = record_count + 1
            except KeyError:
                pass

        return fieldassays

def field_schemas_get_logic(neo4j_instance, field_name=None, mapping_source=None, schema=None) -> List[FieldSchema]:
    """
    Returns detailed information on an ingest metadata field's associated schemas or CEDAR templates.

    :param neo4j_instance: neo4j connection to the UBKG
    :param field_name: name of field for filtered route
    :param mapping_source: name of source of field-schema mapping (HMFIELD or CEDAR)
    :param schema: name of schema from querystring

    """
    # response list
    fieldschemas: [FieldSchema] = []

    # Used in WHERE clauses when no filter is needed.
    identity_filter = '1=1'

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'fieldschemas.cypher'
    query = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    query = query.replace('$field_filter', field_filter)

    # Allow for filtering on schema.
    if schema is None:
        schema_filter = " AND " + identity_filter
    else:
        schema_filter = f" AND tSchema.name = '{schema}'"
    query = query.replace('$schema_filter', schema_filter)

    # Allow for filtering on mapping source.
    if mapping_source is None:
        mapping_source_filter = " AND " + identity_filter
    else:
        mapping_source_filter = f" AND SPLIT(schema_name,'|')[0]='{mapping_source}'"
    query = query.replace('$mapping_source_filter', mapping_source_filter)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        record_count = 0

        # Build response object.
        for record in recds:
            try:
                fieldschema: FieldSchema = \
                    FieldSchema(code_ids=record.get('code_ids'),
                                name=record.get('field_name'),
                                schemas=record.get('schemas')).serialize()

                fieldschemas.append(fieldschema)
                record_count = record_count + 1
            except KeyError:
                pass

        return fieldschemas


def field_entities_get_logic(neo4j_instance, field_name=None, source=None, entity=None, application=None) -> List[FieldEntity]:
    """
    Returns detailed information on an ingest metadata field's associated entities.

    March 2024 - updated to reflect new CEDAR template data and CEDAR_ENTITY ontology.

    :param neo4j_instance: neo4j connection to UBKG
    :param field_name: name of the metadata field
    :param source: name of the source of field-entity mapping--i.e., HMFIELD or CEDAR
    :param entity: term for the entity--e.g., "umi_offset"
    :param application: application context--i.e., HUBMAP or SENNET
    """
    # response list
    fieldentities: [FieldEntity] = []

    # Used in WHERE clauses when no filter is needed.
    identity_filter = '1=1'

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'fieldentities.cypher'
    query = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    query = query.replace('$field_filter', field_filter)

    # Allow for filtering on source.
    if source is None:
        source_filter = "''"
    elif source in ['HMFIELD', 'CEDAR']:
        source_filter = f"'{source}'"
    else:
        source_filter = "''"
    query = query.replace('$source_filter', source_filter)

    # Allow for filtering on entity.
    if entity is None:
        entity_filter = f"AND {identity_filter}"
    else:
        entity_filter = f"AND (tEntity.name='{entity}' OR tEntity.name='{entity}')"
    query = query.replace('$entity_filter', entity_filter)

    # Allow for filtering on application context.
    if application is None:
        application_filter = f"AND cEntity.SAB IN ['HUBMAP','SENNET']"
    else:
        application_filter = f"AND cEntity.SAB='{application}'"
    query = query.replace('$application_filter', application_filter)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        recds: neo4j.Result = session.run(query)

        record_count = 0

        # Build response object.
        for record in recds:
            try:
                fieldentity: FieldEntity = \
                    FieldEntity(code_ids=record.get('code_ids'),
                                name=record.get('field_name'),
                                entities=record.get('entities')).serialize()

                fieldentities.append(fieldentity)
                record_count = record_count + 1

            except KeyError:
                pass

        return fieldentities
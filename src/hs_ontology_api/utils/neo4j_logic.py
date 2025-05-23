# MAR 2025
# Added check for timeout

import logging
import neo4j
from typing import List
import os

# Mar 2025 for handling configurable timeouts
from werkzeug.exceptions import GatewayTimeout

# Classes for JSON objects in response body
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

# Mar 2025
# Until the ubkg-api is refactored so that format_list_for_query function is in
# a utility module, import from the ubkg-api's common_neo4j_logic module.
from ubkg_api.common_routes.common_neo4j_logic import format_list_for_query

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

def get_organ_types_logic(neo4j_instance, sab):
    """
    Objectives: Provide crosswalk information between organs and RUI.
    Replicates the call  original organ_types.yaml.

    :param sab: SAB for application context
    :param neo4j_instance: pointer to neo4j connection
    :return:

    JAS SEPT 2024 - Converted to using JSON returned from query. Added organ category and laterality.

    JAS NOV 2023 - Moved query string to external file and implemented loadquery utility logic.
    """
    result = []

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $sab.
    queryfile = 'organs.cypher'
    querytxt = loadquerystring(queryfile)
    querytxt = querytxt.replace('$sab', f'\'{sab}\'')

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        try:
            recds: neo4j.Result = session.run(query)

            for record in recds:
                result.append(record.get('organ'))

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt: str = "CALL {" \
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

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        try:
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
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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

    querytxt: str = 'CALL'
    querytxt = querytxt + '{'
    # JAS Nov 2023 limit SABs for isa relationship to specified child values
    querytxt = querytxt + 'MATCH (codeChild:Code)<-[:CODE]-(conceptChild:Concept)-[r:isa]->(conceptParent:Concept)-[' \
                    ':CODE]->(codeParent:Code) '
    querytxt = querytxt + ' WHERE codeParent.SAB=\'' + parent_sab + '\' AND codeParent.CODE=\'' + parent_code + '\''
    querytxt = querytxt + ' AND codeChild.SAB IN ' + sab_in
    # JAS Nov 2023 limit SABs for isa relationship to specified child values
    querytxt = querytxt + ' AND r.SAB IN ' + sab_in
    querytxt = querytxt + ' RETURN conceptChild.CUI AS conceptChildCUI, min(' + sab_case + ') AS minSAB'
    querytxt = querytxt + ' ORDER BY conceptChildCUI'
    querytxt = querytxt + '}'

    # 4. Filter to the code for the child concepts with the "earliest" SAB. The "earliest" SAB will be different for
    #    each child concept.  Limit to 1 to account for multiple cross-references (e.g., UMLS C0026018, which maps
    #    to 2 NCI codes).
    querytxt = querytxt + ' CALL'
    querytxt = querytxt + '{'
    querytxt = querytxt + 'WITH conceptChildCUI, minSAB '
    querytxt = querytxt + 'MATCH (codeChild:Code)<-[:CODE]-(conceptChild:Concept) '
    querytxt = querytxt + 'WHERE conceptChild.CUI = conceptChildCUI '
    querytxt = querytxt + 'AND ' + sab_case + ' = minSAB '
    querytxt = querytxt + 'RETURN codeChild '
    querytxt = querytxt + 'ORDER BY codeChild.CODE '
    querytxt = querytxt + 'LIMIT 1'
    querytxt = querytxt + '} '

    # 5. Get the term associated with the child concept code with the earliest SAB.
    querytxt = querytxt + 'WITH codeChild,conceptChildCUI '
    querytxt = querytxt + 'MATCH (termChild:Term)<-[r:PT]-(codeChild:Code) '
    querytxt = querytxt + 'WHERE r.CUI = conceptChildCUI '
    querytxt = querytxt + 'RETURN termChild.name AS term, codeChild.CODE as code,codeChild.SAB as sab'

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    # Execute Cypher query and return result.
    with neo4j_instance.driver.session() as session:
        try:
            recds: neo4j.Result = session.run(query)
            for record in recds:
                try:
                    sabcodeterm: [SabCodeTerm] = SabCodeTerm(record.get('sab'), record.get('code'),
                                                             record.get('term')).serialize()
                    sabcodeterms.append(sabcodeterm)
                except KeyError:
                    pass
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

    querytxt = querytxt.replace('$ids', f'\'{gene_id}\'')

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
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
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)
    starts_with_clause = ''
    if starts_with != '':
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f'AND toUpper(tGene.name) STARTS WITH "{starts_with.upper()}"'
    querytxt = querytxt.replace('$starts_with_clause', starts_with_clause)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
            recds: neo4j.Result = session.run(query)

            for record in recds:
                try:
                    gene_count = record.get('genelistcount')
                except KeyError:
                    pass
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

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
        # Apr 2024 - expanded to case-insensitive search on symbol or name.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f'AND toUpper(map["approved_symbol"][0]) STARTS WITH "{starts_with.upper()}"'

    querytxt = querytxt.replace('$starts_with_clause', starts_with_clause)
    querytxt = querytxt.replace('$skiprows', str(skiprows))
    querytxt = querytxt.replace('$limitrows', str(genes_per_page))

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
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
            genelist: GeneList = GeneList(page=page, total_pages=total_pages, genes_per_page=genes_per_page,
                                          genes=genes, starts_with=starts_with, gene_count=gene_count).serialize()
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

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
    querytxt = querytxt.replace('$starts_with_clause', starts_with_clause)
    querytxt = querytxt.replace('$skiprows', str(skiprows))
    querytxt = querytxt.replace('$limitrows', str(proteins_per_page))

    # If the starts_with parameter is specified, indicate in the response that the search is case-insensitive.
    if starts_with != '':
        starts_with = f'{starts_with} (case-insensitive)'

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
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
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)
    starts_with_clause = ''
    if starts_with != '':
        # Check for recommended_name, entry_name, or one of the list of symbols.
        # (Symbols will not be available until the UNIPROTKB ETL bug with synonyms with parentheses is fixed.)
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f' AND (toLower(id) STARTS WITH "{starts_with.lower()}" ' \
                             f' OR toLower(map["entry_name"][0]) STARTS WITH "{starts_with.lower()}" ' \
                             f' OR toLower(map["recommended_name"][0]) STARTS WITH "{starts_with.lower()}") ' \
                             f' OR ANY (n in map["synonyms"] WHERE n[0].name STARTS WITH "{starts_with.lower()}")'

    querytxt = querytxt.replace('$starts_with_clause', starts_with_clause)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
            recds: neo4j.Result = session.run(query)

            for record in recds:
                try:
                    protein_count = record.get('proteinlistcount')
                except KeyError:
                    pass
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

    querytxt = querytxt.replace('$ids', f'\'{protein_id}\'')

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
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

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)
    starts_with_clause = ''
    if starts_with != '':
        # Check for preferred term or synonym.
        # Escape apostrophes and double quotes.
        starts_with = starts_with.replace("'", "\'").replace('"', "\'")
        starts_with_clause = f' AND toLower(t.name) STARTS WITH "{starts_with.lower()}"' \

    querytxt = querytxt.replace('$starts_with_clause', starts_with_clause)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
            recds: neo4j.Result = session.run(query)

            for record in recds:
                try:
                    celltype_count = record.get('celltypelistcount')
                except KeyError:
                    pass

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

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

    querytxt = querytxt.replace('$starts_with_clause', starts_with_clause)
    querytxt = querytxt.replace('$skiprows', str(skiprows))
    querytxt = querytxt.replace('$limitrows', str(cell_types_per_page))

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with (neo4j_instance.driver.session() as session):
        # Execute Cypher query.
        try:
            recds: neo4j.Result = session.run(query)

            cell_types: [CelltypesListDetail] = []
            # Build the list of gene details for this page.
            for record in recds:
                try:
                    cell_type: CelltypesListDetail = CelltypesListDetail(id=record.get('id'),
                                                                         term=record.get('term'),
                                                                         synonyms=record.get('synonyms'),
                                                                         definition=record.get('definition')).serialize()
                    cell_types.append(cell_type)
                except KeyError:
                    pass

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

    querytxt = querytxt.replace('$ids', f'\'{cl_id}\'')

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        try:
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

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    querytxt = querytxt.replace('$field_filter', field_filter)

    # Allow for filtering on description source
    if definition_source is None:
        source_filter = " AND d.SAB IN ['HMFIELD', 'CEDAR'] "
    elif definition_source in ['HMFIELD', 'CEDAR']:
        source_filter = f" AND d.SAB = '{definition_source}'"
    else:
        source_filter = " AND d.SAB IN ['HMFIELD', 'CEDAR'] "

    querytxt = querytxt.replace('$source_filter', source_filter)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
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

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    querytxt = querytxt.replace('$field_filter', field_filter)

    # Allow for filtering on mapping source.
    if mapping_source is None:
        mapping_source_filter = " AND rdt.SAB IN ['HMFIELD', 'CEDAR'] "
    elif mapping_source in ['HMFIELD', 'CEDAR']:
        mapping_source_filter = f" AND rdt.SAB = '{mapping_source}'"
    else:
        mapping_source_filter = " AND rdt.SAB IN ['HMFIELD', 'CEDAR'] "
    querytxt = querytxt.replace('$mapping_source_filter', mapping_source_filter)

    # Allow for filtering on type source.
    if type_source is None:
        type_source_filter = " AND cType.SAB IN ['HMFIELD', 'XSD'] "
    elif type_source in ['HMFIELD', 'XSD']:
        type_source_filter = f" AND cType.SAB = '{type_source}'"
    else:
        type_source_filter = " AND cType.SAB IN ['HMFIELD', 'XSD'] "
    querytxt = querytxt.replace('$type_source_filter', type_source_filter)

    # Allow for filtering on type.
    if type is None:
        type_filter = f"AND {identity_filter}"
    else:
        type_filter = f"AND CASE WHEN tType.name CONTAINS ':' THEN split(tType.name,':')[1] " \
                      f"ELSE tType.name END='{type}'"
    querytxt = querytxt.replace('$type_filter', type_filter)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
            recds: neo4j.Result = session.run(query)

            record_count = 0
            # Build response object.
            for record in recds:
                try:
                    fieldtype: FieldType = FieldType(code_ids=record.get('code_ids'),
                                                     name=record.get('field_name'),
                                                     types=record.get('types')).serialize()

                    fieldtypes.append(fieldtype)
                    record_count = record_count + 1
                except KeyError:
                    pass

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

    # Allow for filtering on type source.
    if type_source is None:
        type_source_filter = " AND cType.SAB IN ['HMFIELD', 'XSD'] "
    elif type_source in ['HMFIELD', 'XSD']:
        type_source_filter = f" AND cType.SAB = '{type_source}'"
    else:
        type_source_filter = " AND cType.SAB IN ['HMFIELD', 'XSD'] "
    querytxt = querytxt.replace('$type_source_filter', type_source_filter)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
            recds: neo4j.Result = session.run(query)

            # Build response object.
            for record in recds:
                try:
                    fieldtypedetail: FieldTypeDetail = \
                    FieldTypeDetail(type_detail=record.get('type'),
                                    is_mapped=False).serialize()

                    fieldtypes.append(fieldtypedetail)

                except KeyError:
                    pass
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

    return fieldtypes


def field_assays_get_logic(neo4j_instance, field_name=None, assaytype=None) -> dict:
    """
    Returns detailed information on the associations between a  metadata field and assay datasets.
    :param neo4j_instance: connection to UBKG instance
    :param field_name: optional filter: name of field
    :param assaytype: optional filter: name of assay_identifier used in legacy field_assays.yaml. Although
    the legacy yaml allows for alt-names and descriptions, these are no longer valid.
    :return:
    """

    # response list
    fieldassays: [dict] = []

    # Used in WHERE clauses when no filter is needed.
    identity_filter = '1=1'

    # Load annotated Cypher query from the cypher directory.
    # The query is parameterized with variable $ids.
    queryfile = 'fieldassays.cypher'
    querytxt = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    querytxt = querytxt.replace('$field_filter', field_filter)

    # Allow for filtering on assaytype.
    if assaytype is None:
        assay_type_filter = f'AND {identity_filter}'
    else:
        assay_type_filter = f" AND tAssayType.name='{assaytype}'"

    querytxt = querytxt.replace('$assay_type_filter', assay_type_filter)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
            recds: neo4j.Result = session.run(query)

            for field in recds:
                resp = field.get('fieldassays')
                try:
                    fieldassays.append(resp)

                except KeyError:
                    pass

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

        return resp

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
    querytxt = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    querytxt = querytxt.replace('$field_filter', field_filter)

    # Allow for filtering on schema.
    if schema is None:
        schema_filter = " AND " + identity_filter
    else:
        schema_filter = f" AND tSchema.name = '{schema}'"
    querytxt = querytxt.replace('$schema_filter', schema_filter)

    # Allow for filtering on mapping source.
    if mapping_source is None:
        mapping_source_filter = " AND " + identity_filter
    else:
        mapping_source_filter = f" AND SPLIT(schema_name,'|')[0]='{mapping_source}'"
    querytxt = querytxt.replace('$mapping_source_filter', mapping_source_filter)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)
    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
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

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

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
    querytxt = loadquerystring(queryfile)

    # Allow for filtering on field name.
    if field_name is None:
        field_filter = f' AND {identity_filter}'
    else:
        field_filter = f" AND tField.name = '{field_name}'"
    querytxt = querytxt.replace('$field_filter', field_filter)

    # Allow for filtering on source.
    if source is None:
        source_filter = "''"
    elif source in ['HMFIELD', 'CEDAR']:
        source_filter = f"'{source}'"
    else:
        source_filter = "''"
    querytxt = querytxt.replace('$source_filter', source_filter)

    # Allow for filtering on entity.
    if entity is None:
        entity_filter = f"AND {identity_filter}"
    else:
        entity_filter = f"AND (tEntity.name='{entity}' OR tEntity.name='{entity}')"
    querytxt = querytxt.replace('$entity_filter', entity_filter)

    # Allow for filtering on application context.
    if application is None:
        application_filter = f"AND cEntity.SAB IN ['HUBMAP','SENNET']"
    else:
        application_filter = f"AND cEntity.SAB='{application}'"
    querytxt = querytxt.replace('$application_filter', application_filter)

    # March 2025
    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        # Execute Cypher query.
        try:
            recds: neo4j.Result = session.run(query)
            record_count = 0

            # Build response object.
            for record in recds:
                try:
                    fieldentity: FieldEntity = FieldEntity(code_ids=record.get('code_ids'),
                                                           name=record.get('field_name'),
                                                           entities=record.get('entities')).serialize()

                    fieldentities.append(fieldentity)
                    record_count = record_count + 1

                except KeyError:
                    pass

        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

        return fieldentities

def assayclasses_get_logic(neo4j_instance,assayclass=None, assaytype=None, process_state=None,
                           context=None, provide_hierarchy_info=None) -> dict:
    """
    October 2024 - filter response for hierarchical information.

    July 2024
        Obtains information on the assay classes (rule-based dataset "kinds") that are specified in
        the testing rules json file.

        The return from the query is a complete JSON, so there is no need for a model class.

        :param neo4j_instance: neo4j connection
        :param assayclass: either the code for the assay class's rule or the value of rule_description
        :param assaytype: the assaytype
        :param context: application context--i.e., HUBMAP or SENNET
        :param process_state: in the enum ['primary','derived','epic']
        :param provide_hierarchy_info: "string boolean" (i.e. the word "True" or "False") indicating
                                        whether to include dataset hierarchical information in response

        example: if a assay class's rule has rule_description="non-DCWG primary AF" and rule code "HUBMAP:C200001", either
        "non-DCWG primary AF" or "C200001" will result in selection of the assay class. The application context is used
        to identify the complete rule code.

        """
    assayclasses: [dict] = []

    # Load and parameterize query.
    querytxt = loadquerystring('assayclass.cypher')

    # Filter by application context.
    querytxt = querytxt.replace('$context', context)

    # Oct 2024 - Filter by dataset hierarchy.
    querytxt = querytxt.replace('$provide_hierarchy_info', provide_hierarchy_info)

    # Filter by assay class
    if assayclass is not None:
        querytxt = querytxt.replace('$assayclass_filter', f"AND (cRBD.CodeID = context+':{assayclass}' OR tRBD.name='{assayclass}')")
    else:
        querytxt = querytxt.replace('$assayclass_filter','')

    # Filter by process_state
    if process_state is None:
        querytxt = querytxt.replace('$process_state_filter','')
    else:
        querytxt = querytxt.replace('$process_state_filter',f"AND tdsProcess.name='{process_state}'")

    # Filter by assaytype, but only if this is the general endpoint.
    #(The endpoint that filters by assayclass assumes a single response; assaytype is not unique.)
    if assaytype is None:
        querytxt = querytxt.replace('$assaytype_filter','')
    elif assayclass is None:
        querytxt = querytxt.replace('$assaytype_filter', f"AND REPLACE(tassaytype.name,'_assaytype','') = '{assaytype}'")
    else:

        querytxt = querytxt.replace('$assaytype_filter','')

    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        try:
            recds: neo4j.Result = session.run(query)
            for record in recds:
                assayclass = record.get('rule_based_datasets')
                try:
                    assayclasses.append(assayclass)

                except KeyError:
                    pass
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

    return assayclasses

def datasettypes_get_logic(neo4j_instance,datasettype=None, context=None, isepic=None) -> dict:
    """
    July 2024
        Obtains information on dataset types.

        The return from the query is a complete JSON, so there is no need for a model class.

        :param neo4j_instance: neo4j connection
        :param datasettype: dataset_type
        :param context: application context--i.e., HUBMAP or SENNET
        :param isepic: optional filter to Epic (externally processed) dataset types

        """
    datasettypes: [dict] = []

    # Load and parameterize query.
    querytxt = loadquerystring('datasettypes.cypher')

    # Filter by application context.
    querytxt = querytxt.replace('$context', context)

    # Filter by dataset type
    if datasettype is not None:
        querytxt = querytxt.replace('$datasettype_filter', f"AND tDatasetType.name='{datasettype}'")
    else:
        querytxt = querytxt.replace('$datasettype_filter','')

    if isepic in ['true','false']:
        if isepic == 'true':
            isepicbool = True
        else:
            isepicbool = False
        querytxt = querytxt.replace('$epictype_filter', f"WHERE is_externally_processed={isepicbool}")
    else:
        querytxt = querytxt.replace('$epictype_filter','')

    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        try:
            recds: neo4j.Result = session.run(query)

            for record in recds:
                dst = record.get('dataset_types')
                try:
                    datasettypes.append(dst)
                except KeyError:
                    pass
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

    return datasettypes

def pathway_events_with_genes_get_logic(neo4j_instance, geneids=None, pathwayid=None,
                      pathwaynamestartswith=None, eventtypes=None) -> List[dict]:
    """
    March 2025
    Returns detailed information on the set of Reactome pathway events that
    have specified genes as participants.

    :param neo4j_instance: instance of neo4j connection
    :param geneids: optional filter: set of HGNC identifiers
    :param pathwayid: optional filter: Reactome stable id for an event
    :param pathwaynamestartswith: optional filter: partial name for a Reactome event
                                   to be used in 'starts with' queries
    :param eventtypes: optional filter: list of Reactome event types

    """

    events:[dict] = []
    # Load query.
    querytxt = loadquerystring('pathwayevents_with_genes.cypher')

    # Pass parameters to query.
    # geneids is, in general, a list.

    if geneids is None:
        geneidsjoin = f"['']"
    else:
        geneidsjoin = format_list_for_query(listquery=geneids, doublequote=False)
    querytxt = querytxt.replace('$geneids', geneidsjoin)

    if pathwayid is None:
        querytxt = querytxt.replace('$pathwayid',"''")
    else:
        querytxt = querytxt.replace('$pathwayid', f"'{pathwayid}'")

    if pathwaynamestartswith is None:
        querytxt = querytxt.replace('$pathwayname',"''")
    else:
        querytxt = querytxt.replace('$pathwayname', f"'{pathwaynamestartswith}'")

    # eventtypes is, in general, a list.
    if eventtypes is None:
        eventtypesjoin = f"['']"
    else:
        eventtypesjoin = format_list_for_query(listquery=eventtypes, doublequote=False)

    querytxt = querytxt.replace('$eventtypes', eventtypesjoin)

    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        try:
            recds: neo4j.Result = session.run(query)

            for record in recds:
                resp = record.get('response')
                try:
                    events.append(resp)
                except KeyError:
                    pass
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

    # The return should be a list with only one element.
    if len(events)>0:
        return events[0]

def pathway_participants_get_logic(neo4j_instance, pathwayid=None, sabs=None,
                                   featuretypes=None) -> List[dict]:
    """
    March 2025
    Returns detailed information on the set of Reactome pathway events that
    have specified genes as participants.

    :param neo4j_instance: instance of neo4j connection
    :param pathwayid: required filter: Reactome event identifier, which can be:
                                       1. Reactome stable id
                                       2. Leading characters of the event name
    :param sabs: optional filter: list of SABs for participants
    :param featuretypes: optional filter - list of feature types for ENSEMBL participants.
                                            The available feature types are from GENCODE, and
                                            are:
                                            1. gene
                                            2. transcript

    """

    participants:[dict] = []

    # Load query.
    querytxt = loadquerystring('pathwayparticipants.cypher')

    # Pass parameters to query.

    if pathwayid is None:
        querytxt = querytxt.replace('$pathwayid',"''")
    else:
        querytxt = querytxt.replace('$pathwayid', f"'{pathwayid}'")

    if sabs is None:
        sabsjoin = f"['']"
    else:
        sabsjoin = format_list_for_query(listquery=sabs, doublequote=False)

    querytxt = querytxt.replace('$sabs', sabsjoin)

    if featuretypes is None:
        featuretypesjoin = f"['']"
    else:
        featuretypesjoin = format_list_for_query(listquery=featuretypes, doublequote=False)
    querytxt = querytxt.replace('$featuretypes', featuretypesjoin)

    # Set timeout for query based on value in app.cfg.
    query = neo4j.Query(text=querytxt, timeout=neo4j_instance.timeout)

    with neo4j_instance.driver.session() as session:
        try:
            recds: neo4j.Result = session.run(query)

            for record in recds:
                resp = record.get('response')
                try:
                    participants.append(resp)
                except KeyError:
                    pass
        except neo4j.exceptions.ClientError as e:
            # If the error is from a timeout, raise a HTTP 408.
            if e.code == 'Neo.ClientError.Transaction.TransactionTimedOutClientConfiguration':
                raise GatewayTimeout

    if len(participants) > 0:
        return participants[0]
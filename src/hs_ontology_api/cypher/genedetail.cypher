// GENE DETAIL
// Return detailed information on a gene, based on a input list of HGNC identifiers.
// Used by the gene endpoint.

CALL

// Get CUIs of concepts for genes that match the criteria.

{

// Criteria: list of HGNC identifiers.

// The following types of identifiers can be used in the list:
// 1. HGNC numeric IDs (e.g., 7178)
// 2. HGNC approved symbols (e.g., MMRN1)
// 3. HGNC previous symbols (e.g., MMRN)
// 4. HGNC aliases (e.g., ECM)
// 5. names (approved name, previous name, alias name). Because exact matches would be required, it is unlikely that names would be useful criteria.

// If no criteria are specified, return information on all HGNC genes.

//WITH ['60','MMRN1'] AS ids

// The calling function in neo4j_logic.py will replace $ids.
WITH [$ids] AS ids

// Find CUIs for genes that satisfy criteria for HGNC ID or term (symbol, name). The preferred CUI for each HGNC Code can be identified by the CUI property of any relationship between the code and one of its terms--e.g., PT.
OPTIONAL MATCH (pGene:Concept)-[:CODE]->(cGene:Code)-[r]->(tGene:Term) WHERE r.CUI=pGene.CUI AND type(r) IN ['PT','ACR','NS','NP','SYN','NA_UBKG'] AND cGene.SAB='HGNC' AND CASE WHEN ids[0]<>'' THEN (ANY(id IN ids WHERE cGene.CODE=id) or ANY(id in ids WHERE tGene.name=id)) ELSE 1=1 END RETURN DISTINCT pGene.CUI AS GeneCUI

}

CALL{

// Gene symbols, names, aliases, prior values
WITH GeneCUI
OPTIONAL MATCH (pGene:Concept)-[:CODE]->(cGene:Code)-[r]->(tGene:Term) WHERE pGene.CUI=GeneCUI AND r.CUI=pGene.CUI AND type(r) IN ['PT','ACR','NS','NP','SYN','NA_UBKG'] AND cGene.SAB='HGNC' RETURN toInteger(cGene.CODE) AS hgnc_id, CASE type(r) WHEN 'PT' THEN 'approved_name' WHEN 'ACR' THEN 'approved_symbol' WHEN 'NS' THEN 'previous_symbols' WHEN 'NP' THEN 'previous_names' WHEN 'SYN' THEN 'alias_symbols' WHEN 'NA_UBKG' THEN 'alias_names' ELSE type(r) END AS ret_key,tGene.name AS ret_value
ORDER BY hgnc_id, ret_key

UNION

// References to other vocabularies (Entrez, Ensembl, OMIM)
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:CODE]->(cRef:Code) WHERE pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND cRef.SAB IN ['ENTREZ','ENSEMBL','OMIM'] RETURN toInteger(cGene.CODE) as hgnc_id, 'references' AS ret_key, cRef.CodeID AS ret_value
ORDER BY hgnc_id, ret_key

UNION

// References to HUGO (HGNC)
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept) WHERE pGene.CUI=GeneCUI AND cGene.SAB='HGNC' RETURN toInteger(cGene.CODE) as hgnc_id, 'references' AS ret_key, cGene.CodeID AS ret_value
ORDER BY hgnc_id, ret_key

UNION

// References to gene products of genes from UNIPROTKB
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:has_gene_product]->(pProtein:Concept)-[:CODE]->(cProtein:Code) WHERE pGene.CUI=GeneCUI AND cGene.SAB='HGNC' RETURN toInteger(cGene.CODE) AS hgnc_id, 'references' AS ret_key, cProtein.CodeID AS ret_value
ORDER BY hgnc_id,ret_key

UNION

// RefSeq summaries, with backslashes in text replaced with forward slashes
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:DEF]->(dGene:Definition) WHERE pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND dGene.SAB='REFSEQ' RETURN toInteger(cGene.CODE) AS hgnc_id, 'summary' AS ret_key, replace(dGene.DEF,'\\','/') AS ret_value
ORDER BY hgnc_id,ret_key

// CELL TYPE INFORMATION
// Gene to cell type mappings are from the Human Reference Atlas (HRA).
// Cell type information is flattened because a gene can associate with multiple cell types.
// Properties of cell type (from Cell Ontology) except for code are optional.
// Each property will be a list keyed with the CL code--e.g., CL:code1|property,CL:code2|property
// A script can split the lists in each of the cell_type fields and find all properties for a particular CL

UNION

//Cell types - CL Codes
// APRIL 2024 - HRA changed "has_marker_component" to "characterized_by"
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:inverse_characterized_by]->(pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term) WHERE pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND cCL.SAB='CL' AND rCL.CUI=pCL.CUI  RETURN toInteger(cGene.CODE) AS hgnc_id, 'cell_types_code' AS  ret_key, cCL.CodeID AS ret_value
ORDER BY  hgnc_id,ret_key,ret_value

UNION

// Cell types - CL Code|preferred term
// CL codes can be ingested as part of the ingestion of other ontologies in UBKG (e.g. UBERON).
// A CL code may have multiple terms of type "PT".
// If a CL code was ingested as part of CL, then there will be a PT code; if not, then there may be one or more terms of type PT_SAB--e.g.,  PT_UBERON is the preferred term for the CL code ingested with UBERON.
// The preferred term will be the term of type PT; if there is no PT, then any of the others of type PT_SAB will do.

// First, order the preferred terms by whether they are the PT or a PT_SAB.
// APRIL 2024 - HRA changed the label from "has_marker_component" to "characterized_by"
WITH GeneCUI
CALL{
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:inverse_characterized_by]->(pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term) WHERE pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND cCL.SAB='CL' AND rCL.CUI=pCL.CUI AND type(rCL) STARTS WITH 'PT' RETURN toInteger(cGene.CODE) AS hgnc_id, cCL.CodeID AS CLID, MIN(CASE WHEN type(rCL)='PT' THEN 0 ELSE 1 END) AS mintype order by hgnc_id,CLID,mintype
}

// Next, filter to either the PT or one of the PT_SABs.
// MARCH 2024 - WITH used in return to upgrade to v5 Cypher.
WITH hgnc_id, CLID, mintype
OPTIONAL MATCH (cCL:Code)-[rCL]->(tCL:Term)
where cCL.CodeID = CLID AND type(rCL) STARTS WITH 'PT'
AND CASE WHEN type(rCL)='PT' THEN 0 ELSE 1 END=mintype
WITH hgnc_id, 'cell_types_name' AS ret_key, CLID +'|'+ CASE WHEN tCL.name IS NULL THEN '' ELSE tCL.name END AS ret_value
RETURN hgnc_id, ret_key, ret_value

UNION

// Cell types - CL code|definition
// Definitions link to Concepts and multiple CL codes can match to the same concept; however, each CL code has a "preferred" CUI, identified by the CUI property of the relationship of any of the code's linked terms.

// MARCH 2024 - final WITH added to work with v5 Cypher
// APRIL 2024 - HRA changed "has_marker_component" to "characterized_by"
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:inverse_characterized_by]->(pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term),(pCL:Concept)-[:DEF]->(dCL:Definition) WHERE rCL.CUI=pCL.CUI AND pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND cCL.SAB='CL' AND dCL.SAB='CL'
WITH toInteger(cGene.CODE) AS hgnc_id,'cell_types_definition' as ret_key, cCL.CodeID + '|'+ dCL.DEF as ret_value
RETURN DISTINCT hgnc_id, ret_key, ret_value
ORDER BY hgnc_id, ret_value

UNION

// Cell types - CL code|Azimuth organ list
// The Azimuth ontology:
// 1. Assigns AZ cell codes to AZ organ codes.
// 2. Assigns CL codes as cross-references to AZ codes.
// 3. Assigns UBERON codes as cross-references to AZ organ codes.
//
// To get organ information, map gene to cell type to organ location.
// APRIL 2024 - HRA changed "has_marker_component" to "characterized_by"
WITH GeneCUI
//First, get Azimuth Codes that are cross-referenced to CL codes. For the case of a CL code being cross-referenced to multiple AZ codes, only one AZ code gets the "preferred" cross-reference to the CL code; however, all AZ codes have a cross-reference to the CL code, so do not check on rAZ.CUI=pCL.CUI.
CALL
{WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:inverse_characterized_by]->(pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term), (pCL:Concept)-[:CODE]->(cAZ:Code)-[rAZ]->(tAZ:Term) WHERE rCL.CUI=pCL.CUI AND pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND cCL.SAB='CL' AND cAZ.SAB='AZ' RETURN DISTINCT toInteger(cGene.CODE) AS hgnc_id,cCL.CodeID as CLID,cAZ.CodeID AS AZID}
//Use the AZ codes to map to concepts that have located_in relationships with AZ organ codes. The AZ organ codes are cross-referenced to UBERON codes. Limit the located_in relationships to those from AZ.
CALL
{WITH AZID
OPTIONAL MATCH (cAZ:Code)<-[:CODE]-(pAZ:Concept)-[rAZUB:located_in]->(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB:PT]->(tUB:Term) WHERE rAZUB.SAB='AZ' AND rUB.CUI=pUB.CUI AND cAZ.CodeID=AZID AND cUB.SAB='UBERON' RETURN cUB.CodeID+'*'+ tUB.name + '' as UBERONID
}

WITH hgnc_id, 'cell_types_organ' as ret_key, CLID,UBERONID, CLID+ '|' + apoc.text.join(COLLECT(DISTINCT UBERONID),",") AS ret_value
RETURN DISTINCT hgnc_id, ret_key, ret_value
ORDER BY hgnc_id, ret_value

// Indicate the source of cell type information.
// APRIL 2024 - HRA changed "has_marker_component" to "characterized_by"
UNION
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:inverse_characterized_by]->(pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term) WHERE rCL.CUI=pCL.CUI AND pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND cCL.SAB='CL' RETURN DISTINCT toInteger(cGene.CODE) AS hgnc_id,'cell_types_source' as ret_key, cCL.CodeID + '|Human Reference Atlas' as ret_value
ORDER BY hgnc_id,cCL.CodeID + '|Human Reference Atlas'

}

// APRIL 2024 bug fix check for null gene before calling fromlists

WITH hgnc_id, ret_key, COLLECT(ret_value) AS values
WHERE hgnc_id IS NOT NULL
WITH hgnc_id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map
RETURN hgnc_id,
map['approved_symbol'] AS approved_symbol,
map['approved_name'] AS approved_name,
map['previous_symbols'] AS previous_symbols,
map['previous_names'] AS previous_names,
map['alias_symbols'] AS alias_symbols,
map['alias_names'] AS alias_names,
map['references'] AS references,
map['summary'] AS summaries,
map['cell_types_code'] AS cell_types_code,
map['cell_types_name'] AS cell_types_code_name,
map['cell_types_definition'] AS cell_types_code_definition,
map['cell_types_organ'] AS cell_types_codes_organ,
map['cell_types_source'] AS cell_types_codes_source

order by hgnc_id

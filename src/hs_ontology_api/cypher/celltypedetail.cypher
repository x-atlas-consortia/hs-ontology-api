// Return detailed inforomation on cell types, based on a input list of AZ terms.


CALL
// Get CUIs of concepts for cell types that match the criteria.

{

// Criteria: Cell Ontology code
//WITH ['0002138'] AS ids
//WITH [''] AS ids

// The calling function in neo4j_logic.py will replace $ids.
WITH [$ids] AS ids

OPTIONAL MATCH (pCL:Concept)-[:CODE]->(cCL:Code) WHERE cCL.SAB='CL' AND CASE WHEN ids[0]<>'' THEN ANY(id in ids WHERE cCL.CODE=id) ELSE 1=1 END RETURN DISTINCT pCL.CUI AS CLCUI
}

CALL
{

// CL codes and preferred term

// Cell types - CL Code|preferred term
// CL codes can be ingested as part of the ingestion of other ontologies in UBKG (e.g. UBERON).
// A CL code may have multiple terms of type "PT".
// If a CL code was ingested as part of CL, then there will be a PT code; if not, then there may be one or more terms of type PT_SAB--e.g.,  PT_UBERON is the preferred term for the CL code ingested with UBERON.
// The preferred term will be the term of type PT; if there is no PT, then any of the others of type PT_SAB will do.

// First, order the preferred terms by whether they are the PT or a PT_SAB.
WITH CLCUI
CALL{
WITH CLCUI
OPTIONAL MATCH (pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term) WHERE pCL.CUI=CLCUI AND cCL.SAB='CL' AND rCL.CUI=pCL.CUI AND type(rCL) STARTS WITH 'PT' RETURN cCL.CodeID AS CLID, MIN(CASE WHEN type(rCL)='PT' THEN 0 ELSE 1 END) AS mintype order by CLID,mintype
}

// Next, filter to either the PT or one of the PT_SABs.
WITH CLID, mintype
OPTIONAL MATCH (cCL:Code)-[rCL]->(tCL:Term)
WHERE cCL.CodeID = CLID AND type(rCL) STARTS WITH 'PT'
AND CASE WHEN type(rCL)='PT' THEN 0 ELSE 1 END=mintype
RETURN cCL.CodeID AS CLID, 'cell_types_name' AS ret_key, CASE WHEN tCL.name IS NULL THEN '' ELSE tCL.name END AS ret_value
ORDER BY CLID

UNION

// Cell types - CL code|definition
// Because definitions link to Concepts and multiple CL codes can match to the same concept, there will be duplicate and extraneous definitions.
// There is currently no way to link the definition to the code, so collect the definitions and take the first one.

WITH CLCUI
OPTIONAL MATCH (pCL:Concept)-[:CODE]->(cCL:Code),(pCL:Concept)-[:DEF]->(dCL:Definition) WHERE pCL.CUI=CLCUI AND cCL.SAB='CL' AND dCL.SAB='CL' RETURN cCL.CodeID AS CLID,'cell_types_definition' as ret_key, COLLECT(DISTINCT dCL.DEF)[0]  as ret_value
ORDER BY CLID

UNION

//CL-HGNC mappings via HRA

//HGNC ID
WITH CLCUI
OPTIONAL MATCH (cCL:Code)<-[:CODE]-(pCL:Concept)-[:has_marker_component]->(pGene:Concept)-[:CODE]->(cGene:Code)-[r]->(tGene:Term)
WHERE pCL.CUI=CLCUI AND cGene.SAB='HGNC' AND r.CUI=pGene.CUI AND cCL.SAB='CL' AND type(r) IN ['ACR','PT']
RETURN distinct cCL.CodeID as CLID, 'cell_types_genes' as ret_key, cGene.CodeID + '|' + apoc.text.join(COLLECT(tGene.name),'|') AS ret_value
ORDER BY CLID, cGene.CodeID + '|' + apoc.text.join(COLLECT(tGene.name),'|')

UNION

// Cell types - CL code|Azimuth organ list
// The Azimuth ontology:
// 1. Assigns AZ cell codes to AZ organ codes.
// 2. Assigns CL codes as cross-references to AZ codes.
// 3. Assigns UBERON codes as cross-references to AZ organ codes.
//
// To get organ information, cell type to organ location.
//First, get Azimuth Codes that are cross-referenced to CL codes. For the case of a CL code being cross-referenced to multiple AZ codes, only one AZ code gets the "preferred" cross-reference to the CL code; however, all AZ codes have a cross-reference to the CL code, so do not check on code:term:concept CUI matching.
WITH CLCUI
CALL
{WITH CLCUI
OPTIONAL MATCH (cCL:Code)<-[:CODE]-(pAZ:Concept)-[rAZUB:located_in]->(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB:PT]->(tUB:Term) WHERE pAZ.CUI=CLCUI AND cCL.SAB='CL' AND rAZUB.SAB='AZ' AND rUB.CUI=pUB.CUI  AND cUB.SAB='UBERON' RETURN cCL.CodeID AS CLID, cUB.CodeID+'*'+ tUB.name + '' as UBERONID
}
WITH CLID, UBERONID
RETURN DISTINCT CLID,'cell_types_organ' as ret_key, CLID+ '|' + apoc.text.join(COLLECT(DISTINCT UBERONID),",")  AS ret_value
ORDER BY CLID, CLID+ '|' + apoc.text.join(COLLECT(DISTINCT UBERONID),",")

}

//Pivot results

WITH CLID, ret_key, COLLECT(ret_value) AS values
WITH CLID,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map
WHERE CLID IS NOT NULL
RETURN CLID,
map['cell_types_name'] AS cell_types_code_name,
map['cell_types_definition'] AS cell_types_definition,
map['cell_types_genes'] AS cell_types_genes,
map['cell_types_organ'] AS cell_types_organs

order by CLID
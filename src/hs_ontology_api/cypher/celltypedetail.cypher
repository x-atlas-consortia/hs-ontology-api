// Return detailed information on cell types, based on a input list of CL codes.

CALL
// Get CUIs of concepts for cell types that match the criteria.

{

// Criteria: Cell Ontology code
//WITH ['0002138'] AS ids
//WITH [''] AS ids

// The calling function in neo4j_logic.py will replace $ids.
WITH [$ids] AS ids

// APRIL 2024 Bug fix to use CodeID instead of CODE for cases of leading zeroes in strings.

// JANUARY 2025 Because PATO and UBERON are ingested prior to CL, some CL codes will associate with multiple concepts.
// Use the concept that is associated with the code during the CL ingestion, which can be identified by the use of a
// preferred term (term of relationship type PT).

OPTIONAL MATCH (pCL:Concept)-[:CODE]->(cCL:Code)-[r:PT]->(tCL:Term)
WHERE r.CUI = pCL.CUI
AND CASE WHEN ids[0]<>'' THEN ANY(id in ids WHERE cCL.CodeID='CL:'+id) ELSE 1=1 END RETURN DISTINCT pCL.CUI AS CLCUI}
CALL
{

// CL CODES AND PREFERRED TERM

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

//CL-HGNC MAPPINGS VIA HRA
// APRIL 2024 - HRA changed "has_marker_component" to "characterized_by"

//HGNC ID
WITH CLCUI
OPTIONAL MATCH (cCL:Code)<-[:CODE]-(pCL:Concept)-[:characterized_by]->(pGene:Concept)-[:CODE]->(cGene:Code)-[r]->(tGene:Term)
WHERE pCL.CUI=CLCUI AND cGene.SAB='HGNC' AND r.CUI=pGene.CUI AND cCL.SAB='CL' AND type(r) IN ['ACR','PT']
WITH COLLECT(tGene.name) AS tgene_names, cGene.CodeID AS cgene_codeid, cCL.CodeID AS ccl_codeid
WITH distinct ccl_codeid AS CLID, 'cell_types_genes' AS ret_key, cgene_codeid+'|'+apoc.text.join(tgene_names,'|') AS ret_value
RETURN CLID, ret_key, ret_value
ORDER BY CLID, ret_value

UNION

// JUNE 2025 - ANNOTATION MAPPINGS TO CELL ONTOLOGY AND UBERON
// Revised:
// 1. To include Azimuth, STELLAR, DeepCellType, and Pan Organ Azimuth
// 2. To account for use of UBERON base ontology instead of UBERON

// Each annotation mapping:
// 1. Assigns annotation cell codes to annotation organ codes.
// 2. Assigns CL codes as cross-references to annotation cell codes.
// 3. Assigns UBERON codes as cross-references to annotation organ codes.

// In addition, Pan Organ Azimuth organizes annotations by "organ level".

// Algorithm:

// 1. Get all annotation cell type codes that are cross-referenced to CL codes.
// For the case of a CL code being cross-referenced to multiple codes from a mapping, only one of the codes gets the "preferred"
// cross-reference to the CL code (via concept mapping); however, all of the mapped codes still have a cross-reference to the CL code.

WITH CLCUI
CALL
{
        WITH CLCUI
        OPTIONAL MATCH (pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term),
        (pCL:Concept)-[:CODE]->(cMap:Code)-[rMap]->(tMap:Term)
        WHERE pCL.CUI=CLCUI AND rCL.CUI=pCL.CUI AND cCL.SAB='CL'
        AND cMap.SAB IN['AZ','STELLAR','DCT','PAZ']
        RETURN DISTINCT cCL.CodeID as CLID,cMap.CodeID AS mapID
}
// 2. Use the annotation cell codes to map to concepts that have located_in relationships with annotation organ codes.
// Annotation organ codes are cross-referenced to UBERON codes.
// Limit the located_in relationships to those from annotation maps.
// For PAZ and downward compatibility, overload the organ code with the PAZ "organ_level" code.

WITH CLID,mapID
CALL
{   WITH mapID
    MATCH (cMap:Code)<-[:CODE]-(pMap:Concept)-[rMapUB:located_in]->(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB]->(tUB:Term)
    WHERE rMapUB.SAB IN ['AZ','STELLAR','DCT']
    AND rUB.CUI=pUB.CUI
    AND cMap.CodeID=mapID
    AND cUB.SAB='UBERON'
    AND TYPE(rUB) STARTS WITH 'PT'
    RETURN cUB.CodeID+'|'+ tUB.name + '|' + rMapUB.SAB as UBERONID

    UNION
    WITH mapID

    MATCH (cMap:Code)<-[:CODE]-(pMap:Concept)-[rMapUB:has_organ_level]->(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB:PT]->(tUB:Term)
    WHERE rMapUB.SAB ='PAZ'
    AND rUB.CUI=pUB.CUI
    AND cMap.CodeID=mapID
    AND cUB.SAB='PAZ'
    RETURN cUB.CodeID+'|'+ tUB.name + '|' + '' as UBERONID
}

WITH CLID,UBERONID
RETURN DISTINCT CLID, 'cell_types_organ' as ret_key, apoc.text.join(COLLECT(DISTINCT UBERONID),",")  AS ret_value
ORDER BY CLID, apoc.text.join(COLLECT(DISTINCT UBERONID),",")

}


//Pivot results

WITH CLID, ret_key, COLLECT(ret_value) AS values
WITH CLID,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map
WHERE CLID IS NOT NULL
RETURN CLID,
map['cell_types_name'] AS cell_types_code_name,
//map['cell_types_definition'] AS cell_types_definition,
//map['cell_types_genes'] AS cell_types_genes,
map['cell_types_organ'] AS cell_types_organs

order by CLID

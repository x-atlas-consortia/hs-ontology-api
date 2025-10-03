// OCTOBER 2025
// Return reference information (terms, definitions) on cell types, based on a input list of CL codes or terms.
// Used by the celltypes/<id> endpoint.

CALL
// Get CUIs of concepts for cell types that match the criteria.

{

// Criteria: Cell Ontology code
//WITH ['0002138','0000236'] AS ids
//WITH [''] AS ids

// The calling function in neo4j_logic.py will replace $ids.
WITH [$ids] AS ids

// Because PATO and UBERON are ingested prior to CL, some CL codes will associate with multiple concepts.
// Use the concept that is associated with the code during the CL ingestion, which can be identified by the use of a
// preferred term (term of relationship type PT).
OPTIONAL MATCH (dCL:Definition {SAB:'CL'})<-[:DEF]-(pCL:Concept)-[:CODE]->(cCL:Code{SAB:'CL'})-[r:PT]->(tCL:Term)
WHERE r.CUI = pCL.CUI
AND CASE WHEN ids[0]<>'' THEN ANY(id in ids WHERE cCL.CodeID='CL:'+id) ELSE 1=1 END
RETURN DISTINCT pCL.CUI AS CLCUI, cCL.CodeID as CLID, tCL.name AS name, COLLECT(dCL.DEF)[0] AS definition
}
WITH CLID, name, definition
WHERE CLID IS NOT NULL

WITH COLLECT({cell_type:{id:CLID,name:name,definition:definition}}) AS celltype
RETURN celltype

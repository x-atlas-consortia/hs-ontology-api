// OCTOBER 2025
// Return reference information (terms, definitions) on cell types, based on a input list of CL codes or search.
// Used by the celltypes/<id> endpoint.

// Returns as JSON.

CALL
// Get CUIs of concepts for cell types that match the criteria.

{

// Criteria: Cell Ontology code
//WITH ['0002138','0000236'] AS ids
//WITH [''] AS ids

// The calling function in neo4j_logic.py will replace $ids.
WITH [$ids] AS ids

// 1. Because PATO and UBERON are ingested prior to CL, some CL codes may associate with multiple concepts.
//    Use the concept that is associated with the code during the CL ingestion, which can be identified by the use of a
//    preferred term (term of relationship type PT).
// 2. If the id is an integer, assume a search on CL ID; otherwise, assume a search on a term.
// 3. Because the definition of a code is associated with the code's concept, there will generally be duplicate definitions per code.
//    Take the first definition in the list.
OPTIONAL MATCH (dCL:Definition {SAB:'CL'})<-[:DEF]-(pCL:Concept)-[:CODE]->(cCL:Code{SAB:'CL'})-[r:PT]->(tCL:Term)
WHERE r.CUI = pCL.CUI
AND (
  ids[0] <> '' AND
  ANY(id IN ids WHERE
    CASE
      WHEN id =~ '^\d+$' THEN
        cCL.CodeID = 'CL:' + id
      ELSE
       tCL.name CONTAINS id
    END
  )
  OR ids[0] = ''
)
RETURN DISTINCT pCL.CUI AS CLCUI, cCL.CodeID as CLID, tCL.name AS name, COLLECT(dCL.DEF)[0] AS definition
}
// Filter out null codes.
WITH CLID, name, definition
WHERE CLID IS NOT NULL
WITH COLLECT({cell_type:{id:CLID,name:name,definition:definition}}) AS celltype
RETURN celltype

// OCTOBER 2025

// Return detailed information on cell types, based on a input list of CL codes.
// Used by the celltypes/<id>/detail route.

// Return detailed information on cell types, based on a input list of CL codes.
// Used by the celltypes/<id>/detail route.

WITH ['AZ','STELLAR','DCTH','PAZ','RIBCA','VCCF'] AS annotation_sabs

// Get CUIs of concepts for cell types that match the criteria.
// Note that this CALL statement is identical to that used by celltype.cypher.
CALL
{

	// Sample Criteria
	//WITH ['0002138','adipose'] AS ids

	// The calling function in neo4j_logic.py will replace $ids.
	WITH [$ids] AS ids

	// 1. Because PATO and UBERON are ingested prior to CL, some CL codes may associate with multiple concepts.
	//    Use the concept that is associated with the code during the CL ingestion, which can be identified by the use of a
	//    preferred term (term of relationship type PT).
	// 2. If the criterion is an integer, assume a search on CL ID; otherwise, assume a search on a term.
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

// DETAILS

//CL-HGNC MAPPINGS VIA HRA, ORDERED BY HGNC ID.
CALL
{
	WITH CLCUI, CLID,name,definition
	OPTIONAL MATCH (cCL:Code{SAB:'CL'})<-[:CODE]-(pCL:Concept{CUI:CLCUI})-[:characterized_by]->(pGene:Concept)-[:CODE]->(cGene:Code{SAB:'HGNC'})-[r]->(tGene:Term)
	WHERE r.CUI=pGene.CUI AND type(r) IN ['ACR']
	WITH COLLECT({reference:'Human Reference Atlas', biomarker_type:'gene', entry:{vocabulary:'hgnc', id:cGene.CodeID, symbol:tGene.name}}) AS biomarker_list
	UNWIND biomarker_list AS biomarker
	WITH biomarker
	ORDER BY biomarker.entry.id
	RETURN COLLECT(biomarker) AS biomarkers

}

// ANNOTATION INFORMATION
// Each annotation mapping:
// 1. Assigns annotation cell codes to annotation "organ level" codes.
// 2. Assigns CL codes as cross-references to annotation cell codes.
// 3. Asserts "part_of" relationships between organ level codes and UBERON organ codes.

//Annotation list
CALL
{
	WITH CLCUI,annotation_sabs
	OPTIONAL MATCH (pCL:Concept{CUI:CLCUI})-[:CODE]->(cAnn:Code)-[rAnn:PT]->(tAnn:Term)
    WHERE cAnn.SAB IN annotation_sabs
    RETURN DISTINCT cAnn.CodeID AS AnnID, tAnn.name AS AnnName
 }

// Organ list
WITH annotation_sabs,CLID, name, definition, biomarkers, AnnID, AnnName
CALL
 {
	 WITH annotation_sabs, AnnID
	 OPTIONAL MATCH (cAnn:Code{CodeID:AnnID})<-[:CODE]-(pAnn:Concept)-[rloc:located_in]->(pOL:Concept)-[:CODE]->(cOL:Code)-[rOL:PT]->(tOL:Term),
	 (pOL:Concept)-[rpart:part_of]->(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB:PT_UBERON_BASE]->(tUB:Term)
	 WHERE cOL.SAB IN annotation_sabs
     AND rOL.CUI=pOL.CUI
	 AND rUB.CUI=pUB.CUI
	 RETURN DISTINCT cOL.CodeID AS OLID, tOL.name AS OLName, cUB.CodeID AS UBID, tUB.name AS UBName, rloc.SAB as OLSAB
 }

WITH annotation_sabs,CLID, name, definition, biomarkers, AnnID, AnnName,OLSAB, OLID,OLName,UBID,UBName
ORDER BY OLID,UBID,AnnID,AnnName
WITH annotation_sabs,CLID, name, definition, biomarkers,
COLLECT(DISTINCT {code:AnnID,term:AnnName}) AS annotations,
COLLECT(DISTINCT {annotation:OLSAB, organ_level_code:OLID,organ_level_term:OLName,uberon_code:UBID, uberon_term:UBName}) AS organs

WITH CLID,name,definition,biomarkers, annotations,organs
WHERE CLID IS NOT NULL
WITH CLID,name,definition,biomarkers, annotations,organs
WITH COLLECT(DISTINCT{cell_type:{id:CLID,name:name,definition:definition},annotations:annotations,organ_levels:organs}) AS celltype
RETURN distinct celltype
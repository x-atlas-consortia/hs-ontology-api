// OCTOBER 2025
// Refactored:
// 1. to use simpler linkage for terms and definitions, taking advantage of reduced
//    ingestion of UBERON and PATO ("base" OWLs)
// 2. to allow text searching on terms
// 3. to return as JSON


// Return detailed information on cell types, based on a input list of CL codes.
// Used by the celltypes/<id>/detail route.

// Get CUIs of concepts for cell types that match the criteria.
// Note that this CALL statement is identical to that used by celltype.cypher.
CALL
{

	// Criteria: Cell Ontology code
	//WITH ['0002138','adipose'] AS ids
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

// DETAILS

//CL-HGNC MAPPINGS VIA HRA, ORDERED BY HGNC ID.
CALL
{
	WITH CLCUI, CLID,name,definition
	OPTIONAL MATCH (cCL:Code)<-[:CODE]-(pCL:Concept)-[:characterized_by]->(pGene:Concept)-[:CODE]->(cGene:Code)-[r]->(tGene:Term)
	WHERE pCL.CUI=CLCUI AND cGene.SAB='HGNC' AND r.CUI=pGene.CUI AND cCL.SAB='CL' AND type(r) IN ['ACR']
	WITH COLLECT({reference:'Human Reference Atlas', biomarker_type:'gene', entry:{vocabulary:'hgnc', id:cGene.CodeID, symbol:tGene.name}}) AS biomarker_list
	UNWIND biomarker_list AS biomarker
	WITH biomarker
	ORDER BY biomarker.entry.id
	RETURN COLLECT(biomarker) AS biomarkers

}

// ORGANS VIA ANNOTATION MAPPINGS
// Each annotation mapping:
// 1. Assigns annotation cell codes to annotation organ codes.
// 2. Assigns CL codes as cross-references to annotation cell codes.
// 3. Assigns UBERON codes as cross-references to annotation organ codes.

// In addition, Pan Organ Azimuth organizes annotations by "organ level".

// FIRST, Get all annotation cell type codes that are cross-referenced to CL codes.
// For the case of a CL code being cross-referenced to multiple codes from a mapping, only one of the codes gets the "preferred"
// cross-reference to the CL code (via concept mapping); however, all of the mapped codes still have a cross-reference to the CL code.
CALL
{
	WITH CLCUI,CLID,name,definition
	OPTIONAL MATCH (pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term),
	(pCL:Concept)-[:CODE]->(cMap:Code)-[rMap]->(tMap:Term)
    WHERE pCL.CUI=CLCUI
    AND rCL.CUI=pCL.CUI
    AND cCL.SAB='CL'
    AND cMap.SAB IN['AZ','STELLAR','DCT','PAZ']
    RETURN DISTINCT cMap.CodeID AS mapID
 }

// SECOND, Use the annotation cell codes to map to concepts that have located_in relationships with annotation organ codes.
// Annotation organ codes are cross-referenced to UBERON codes. Limit the located_in relationships to those from annotation maps.
CALL
{
	WITH CLCUI,CLID,name,definition,mapID
   	OPTIONAL MATCH (cMap:Code)<-[:CODE]-(pMap:Concept)-[rMapUB:located_in]->(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB:PT_UBERON_BASE]->(tUB:Term)
    WHERE rMapUB.SAB IN ['AZ','STELLAR','DCT','PAZ','RIBCA']
    AND rUB.CUI=pUB.CUI
    AND cMap.CodeID=mapID
    AND cUB.SAB='UBERON'
    RETURN cUB.CodeID AS UBCode, tUB.name AS UBName, rMapUB.SAB AS UBAnnotation, 'UBERON' AS source
}

// Collect and order organs by annotation type.
WITH CLID,name,definition,biomarkers, COLLECT(DISTINCT{id:UBCode,name:UBName,source:source,annotation:UBAnnotation}) AS organ_list
WHERE CLID IS NOT NULL
UNWIND organ_list AS organ
WITH CLID,name,definition,biomarkers,organ
ORDER BY organ.annotation
WITH CLID,name,definition,biomarkers,COLLECT(organ) AS organs
WITH COLLECT({cell_type:{id:CLID,name:name,definition:definition,biomarkers:biomarkers,organs:organs}}) AS celltype
RETURN celltype
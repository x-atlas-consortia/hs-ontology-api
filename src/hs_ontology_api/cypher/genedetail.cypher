// GENES detail
// OCTOBER 2025
// Refactored:
// 1. Annotation-related maps to CL take advantage of reduced ingests of UBERON and PATO.
// 2. Returns as JSON


// Return detailed information on a gene, based on a input list of HGNC identifiers.
// Used by the genes endpoint.

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

//WITH ['MMRN1'] AS ids

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
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:DEF]->(dGene:Definition) WHERE pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND dGene.SAB='REFSEQ'
RETURN toInteger(cGene.CODE) AS hgnc_id, 'summary' AS ret_key, replace(dGene.DEF,'\\','/') AS ret_value
ORDER BY hgnc_id,ret_key

UNION

// Cell type assertions from HRA
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:inverse_characterized_by]->(pCL:Concept)-[:CODE]->(cCL:Code)-[rCL:PT]->(tCL:Term),
			(pCL:Concept)-[:DEF]->(dCL:Definition)
WHERE pGene.CUI=GeneCUI
	AND cGene.SAB='HGNC'
	AND cCL.SAB='CL'
	AND rCL.CUI=pCL.CUI
WITH toInteger(cGene.CODE) AS hgnc_id, cCL.CodeID AS CLID, tCL.name AS CLname, COLLECT(DISTINCT dCL.DEF)[0] AS CLdefinition, pCL.CUI AS CLCUI

// Organ assertions from annotations.
// FIRST, Get all annotation cell type codes that are cross-referenced to CL codes.
// For the case of a CL code being cross-referenced to multiple codes from a mapping, only one of the codes gets the "preferred"
// cross-reference to the CL code (via concept mapping); however, all of the mapped codes still have a cross-reference to the CL code.

WITH hgnc_id, CLID, CLname,CLdefinition,CLCUI
OPTIONAL MATCH (pCL:Concept)-[:CODE]->(cCL:Code)-[rCL]->(tCL:Term),
	(pCL:Concept)-[:CODE]->(cMap:Code)-[rMap]->(tMap:Term)
WHERE pCL.CUI=CLCUI
AND rCL.CUI=pCL.CUI
AND cCL.SAB='CL'
AND cMap.SAB IN['AZ','STELLAR','DCT','PAZ']

WITH hgnc_id, CLID, CLname,CLdefinition,CLCUI,cMap.CodeID AS mapID
CALL
	{
		WITH mapID
		OPTIONAL MATCH (cMap:Code)<-[:CODE]-(pMap:Concept)-[rMapUB:located_in]->(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB:PT_UBERON_BASE]->(tUB:Term)
		WHERE rMapUB.SAB IN ['AZ','STELLAR','DCT']
    	AND rUB.CUI=pUB.CUI
    	AND cMap.CodeID=mapID
    	AND cUB.SAB='UBERON'

		RETURN CASE WHEN cUB.CodeID IS NULL THEN NULL ELSE {id:cUB.CodeID,name:tUB.name, annotation:rMapUB.SAB,source:'UBERON'} END AS organ

		UNION

		WITH mapID
    	OPTIONAL MATCH (cMap:Code)<-[:CODE]-(pMap:Concept)-[rMapUB:has_organ_level]->(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB:PT]->(tUB:Term)
    	WHERE rMapUB.SAB ='PAZ'
    	AND rUB.CUI=pUB.CUI
    	AND cMap.CodeID=mapID
    	AND cUB.SAB='PAZ'
    	RETURN CASE WHEN cUB.CodeID IS NULL THEN NULL ELSE {id:cUB.CodeID,name:tUB.name, annotation:rMapUB.SAB,source:'PAZ'} END AS organ

    }

WITH hgnc_id, CLID, CLname,CLdefinition,CLCUI,COLLECT(DISTINCT organ) AS organ_list
UNWIND organ_list AS organ
WITH hgnc_id, CLID, CLname,CLdefinition,CLCUI,organ
ORDER BY organ.annotation,organ.id
WITH hgnc_id, CLID, CLname,CLdefinition,CLCUI,COLLECT(organ) AS organs
RETURN hgnc_id, 'cell_types' AS ret_key, COLLECT(DISTINCT({id:CLID,name:CLname,definition:CLdefinition,organs:organs})) AS ret_value

}

WITH hgnc_id, ret_key, COLLECT(DISTINCT ret_value) AS values
WHERE hgnc_id IS NOT NULL
WITH hgnc_id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map

WITH hgnc_id,
	{
	    hgnc_id:hgnc_id,
		approved_name:map['approved_name'][0],
		approved_symbol:map['approved_symbol'][0],
		previous_symbols:map['previous_symbols'],
		previous_names:map['previous_names'],
		alias_symbols:map['alias_symbols'],
		alias_names:map['alias_names'],
		references:map['references'],
		summary:map['summary'],
		cell_types:map['cell_types'][0]

	} AS gene
WHERE hgnc_id IS NOT NULL

RETURN COLLECT(gene) AS genes

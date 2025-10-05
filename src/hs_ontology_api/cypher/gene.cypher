// GENES
// Return reference information on a gene, based on a input list of HGNC identifiers.
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

// RefSeq summaries, with backslashes in text replaced with forward slashes
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[:DEF]->(dGene:Definition) WHERE pGene.CUI=GeneCUI AND cGene.SAB='HGNC' AND dGene.SAB='REFSEQ' RETURN toInteger(cGene.CODE) AS hgnc_id, 'summary' AS ret_key, replace(dGene.DEF,'\\','/') AS ret_value
ORDER BY hgnc_id,ret_key

}

WITH hgnc_id, ret_key, COLLECT(ret_value) AS values
WHERE hgnc_id IS NOT NULL
WITH hgnc_id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map

WITH hgnc_id,
	{
		approved_name:map['approved_name'][0],
		approved_symbol:map['approved_symbol'][0],
		previous_symbols:map['previous_symbols'],
		previous_names:map['previous_names'],
		alias_symbols:map['alias_symbols'],
		alias_names:map['alias_names'],
		references:map['references'],
		summary:map['summary']

	} AS gene
WHERE hgnc_id IS NOT NULL
RETURN COLLECT(gene) AS genes

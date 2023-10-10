// GENES LIST
// Return information on genes in the UBKG
// Used by the genes_list endpoint.

CALL
{
OPTIONAL MATCH (tGene:Term)<-[r]-(cGene:Code)<-[:CODE]-(pGene:Concept)-[:DEF]->(d:Definition) WHERE r.CUI=pGene.CUI AND cGene.SAB='HGNC' AND d.SAB='REFSEQ' AND type(r) IN ['PT','ACR'] RETURN toInteger(cGene.CODE) AS hgnc_id, CASE type(r) WHEN 'PT' THEN 'approved_name' WHEN 'ACR' THEN 'approved_symbol' ELSE type(r) END AS ret_key, tGene.name AS ret_value, d.DEF AS description
order by hgnc_id,ret_key
}
// Pivot approved_name and approved_symbol.
WITH hgnc_id,ret_key, COLLECT(ret_value) AS values, description
WITH hgnc_id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map, description
WHERE hgnc_id IS NOT NULL
RETURN hgnc_id,
map['approved_symbol'] AS approved_symbol,
map['approved_name'] AS approved_name,
description
ORDER BY approved_symbol
// Pagination parameters to be added by calling function.
SKIP $skiprows
LIMIT $limitrows
// MOUSE GENES LIST
// Return high-level information on genes in the UBKG
// Used by the genes-info endpoint for mouse genes.

CALL
{
OPTIONAL MATCH (tGene:Term)<-[r]-(cGene:Code)<-[:CODE]-(pGene:Concept) WHERE r.CUI=pGene.CUI AND cGene.SAB='MGI' AND type(r) IN ['PT_HCOP','SY'] RETURN toInteger(cGene.CODE) AS mgi_id, CASE type(r) WHEN 'PT_HCOP' THEN 'approved_name' WHEN 'SY' THEN 'approved_symbol' ELSE type(r) END AS ret_key, tGene.name AS ret_value
order by mgi_id,ret_key
}
// Pivot values.
WITH mgi_id,ret_key, COLLECT(ret_value) AS values
WITH mgi_id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map
WHERE mgi_id IS NOT NULL
// Allow for typeahead searches. neo4j_logic will replace $starts_with_clause with a parameterized STARTS WITH clause.
$starts_with_clause
RETURN mgi_id,
map["approved_symbol"] AS approved_symbol,
map['approved_name'] AS approved_name
ORDER BY approved_symbol
// Pagination parameters to be added by calling function.
SKIP $skiprows
LIMIT $limitrows
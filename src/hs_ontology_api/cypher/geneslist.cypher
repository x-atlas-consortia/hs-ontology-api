// GENES LIST
// Return high-level information on genes in the UBKG
// Used by the genes-info endpoint.

// Optional case-insensitive typeahead STARTS WITH parameter provided by route
WITH $starts_with_clause AS starts_with_clause
CALL
{
OPTIONAL MATCH (tGene:Term)<-[r]-(cGene:Code)<-[:CODE]-(pGene:Concept)
  WHERE r.CUI=pGene.CUI
  AND cGene.SAB='HGNC'
  // HGNC gene symbols are of term type ACR.
  AND type(r) IN ['PT','ACR']
RETURN toInteger(cGene.CODE) AS hgnc_id,
       CASE type(r)
         WHEN 'PT' THEN 'approved_name'
         WHEN 'ACR' THEN 'approved_symbol'
         ELSE type(r)
         END AS ret_key,
       tGene.name AS ret_value
order by hgnc_id,ret_key
UNION
OPTIONAL MATCH (d:Definition)<-[:DEF]-(pGene:Concept)-
[:CODE]-(cGene:Code)-[r]->(tGene:Term)
  WHERE r.CUI=pGene.CUI
  AND cGene.SAB='HGNC'
  AND type(r) IN ['ACR']
RETURN toInteger(cGene.CODE) AS hgnc_id,
       'description' AS ret_key,
       d.DEF AS ret_value
ORDER BY hgnc_id, ret_key
}
// Pivot values.
WITH starts_with_clause,hgnc_id,ret_key, COLLECT(ret_value) AS values
WITH starts_with_clause,hgnc_id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map
WHERE hgnc_id IS NOT NULL
// Allow for typeahead searches.
AND
  CASE
    WHEN starts_with_clause = '' THEN 1=1
    // Escape special characters. MGI symbols are bracketed.
    ELSE toUpper(replace(replace(replace(toString(map["approved_symbol"][0]), "[", ""), "]", ""), "\'", ""))
    STARTS WITH toUpper(starts_with_clause)
  END
RETURN hgnc_id,
map['approved_symbol'] AS approved_symbol,
map['approved_name'] AS approved_name,
map['description'] AS description
ORDER BY approved_symbol
// Pagination parameters to be added by calling function.
SKIP $skiprows
LIMIT $limitrows
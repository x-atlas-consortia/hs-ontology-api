// MOUSE GENES LIST
// Return high-level information on genes in the UBKG
// Used by the genes-info endpoint for mouse genes.

// Optional typeahead STARTS WITH parameter provided by route
WITH $starts_with_clause AS starts_with_clause
CALL
{
OPTIONAL MATCH (tGene:Term)<-[r]-(cGene:Code)<-[:CODE]-(pGene:Concept)
  WHERE r.CUI=pGene.CUI
  AND cGene.SAB='MGI'
  // MGI gene symbols are of term type SY.
  AND type(r) IN ['SY','PT_HCOP']
RETURN toInteger(cGene.CODE) AS mgi_id,
       CASE type(r)
         WHEN 'PT_HCOP' THEN 'approved_name'
         WHEN 'SY' THEN 'approved_symbol'
         ELSE type(r) END AS ret_key,
       tGene.name AS ret_value
order by mgi_id,ret_key
}
// Pivot values.
WITH starts_with_clause,mgi_id,ret_key, COLLECT(ret_value) AS values
WITH starts_with_clause,mgi_id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map
WHERE mgi_id IS NOT NULL
// Allow for typeahead searches.
AND
  CASE
    WHEN starts_with_clause = '' THEN 1=1
     // Escape special characters. MGI symbols are bracketed.
    ELSE toUpper(replace(replace(replace(toString(map["approved_symbol"][0]), "[", ""), "]", ""), "\'", ""))
    STARTS WITH toUpper(starts_with_clause)
  END
RETURN mgi_id,
map["approved_symbol"] AS approved_symbol,
map['approved_name'] AS approved_name
ORDER BY approved_symbol
// Pagination parameters to be added by calling function.
SKIP $skiprows
LIMIT $limitrows
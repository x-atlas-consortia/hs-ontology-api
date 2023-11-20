 // Returns count of UNIPROTKB proteins in UBKG.
CALL
{
// Protein identifiers
OPTIONAL MATCH (pProtein:Concept)-[:CODE]->(cProtein:Code)-[r]->(tProtein:Term) WHERE r.CUI=pProtein.CUI AND type(r) IN ['PT','SY'] AND cProtein.SAB='UNIPROTKB' RETURN cProtein.CODE as id, CASE type(r) WHEN 'PT' THEN 'recommended_name' WHEN 'SY' THEN CASE WHEN tProtein.name ENDS WITH '_HUMAN' THEN 'entry_name' ELSE 'synonym' END ELSE 'synonym' END AS ret_key,tProtein.name AS ret_value
ORDER BY id, ret_key
}
//Pivot results
WITH id, ret_key, COLLECT(ret_value) AS values
WITH id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map
WHERE id IS NOT NULL
// Allow for typeahead searches. neo4j_logic will replace $starts_with_clause with a parameterized STARTS WITH clause.
$starts_with_clause
RETURN COUNT(DISTINCT id) AS proteinlistcount
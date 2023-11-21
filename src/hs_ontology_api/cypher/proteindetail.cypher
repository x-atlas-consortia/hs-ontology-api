// Return detailed information on a protein, based on a input list of UniProtKB identifiers.

CALL
// Get CUIs of concepts for proteins that match the criteria.
{
// Criteria: list of UniProtKB identifiers.
// The following types of identifiers can be used in the list:
// 1. UniProtKB IDs (e.g., Q13201)
// 2. UniProtKB Entry Names (e.g., MMRN1_HUMAN)
//
// If no criteria are specified, return information on all UniProtKB proteins.
//WITH ['P53539','MMRN1_HUMAN'] AS ids
// The calling function in neo4j_logic.py will replace $ids.
WITH [$ids] AS ids

OPTIONAL MATCH (pProtein:Concept)-[:CODE]->(cProtein:Code)-[r]->(tProtein:Term)
WHERE r.CUI=pProtein.CUI AND type(r) IN ['PT','SY']
AND cProtein.SAB='UNIPROTKB'
AND (CASE WHEN ids[0]<>'' THEN (ANY(id IN ids WHERE cProtein.CODE=id) or ANY(id in ids WHERE tProtein.name=id)) ELSE 1=1 END)
RETURN DISTINCT pProtein.CUI AS ProteinCUI
}

CALL
{
// Protein names
WITH ProteinCUI
OPTIONAL MATCH (pProtein:Concept)-[:CODE]->(cProtein:Code)-[r]->(tProtein:Term) WHERE pProtein.CUI=ProteinCUI
AND r.CUI=pProtein.CUI AND type(r) IN ['PT','SY']
AND cProtein.SAB='UNIPROTKB' RETURN cProtein.CODE as id, CASE type(r) WHEN 'PT' THEN 'recommended_name' WHEN 'SY' THEN
CASE WHEN tProtein.name ENDS WITH '_HUMAN' THEN 'entry_name' ELSE 'synonym' END ELSE 'synonym' END AS ret_key,
tProtein.name AS ret_value
ORDER BY id, ret_key

UNION

// Definitions
// Because definitions link to Concepts and multiple UNIPROTKB codes can match to the same concept, there will be
// duplicate and extraneous definitions.
// There is currently no way to link the definition to the code, so collect the definitions and take the first one.

WITH ProteinCUI
OPTIONAL MATCH (cProtein:Code)<-[:CODE]-(pProtein:Concept)-[:DEF]->(dProtein:Definition)
WHERE pProtein.CUI=ProteinCUI AND cProtein.SAB='UNIPROTKB'
AND dProtein.SAB='UNIPROTKB'
RETURN cProtein.CODE AS id,'description' as ret_key, COLLECT(DISTINCT dProtein.DEF)[0]  as ret_value
ORDER BY id
}

//Pivot results

WITH id, ret_key, COLLECT(ret_value) AS values
WITH id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map
WHERE id IS NOT NULL
RETURN id,
map['recommended_name'] AS recommended_name,
map['entry_name'] AS entry_name,
map['synonym'] AS synonyms,
map['description'] AS description

order by id
// Returns count of cell types from Cell Ontology in UBKG.
MATCH (t:Term)<-[r]-(c:Code)<-[:CODE]-(p:Concept)
WHERE r.CUI=p.CUI AND c.SAB='CL' AND TYPE(r) IN ['PT','SY']
// Allow for typeahead searches. neo4j_logic will replace $starts_with_clause with a parameterized STARTS WITH clause.
$starts_with_clause
RETURN COUNT(DISTINCT c.CodeID) as celltypelistcount
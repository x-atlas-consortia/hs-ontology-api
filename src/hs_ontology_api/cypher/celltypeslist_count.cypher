// Returns count of cell types from Cell Ontology in UBKG.
WITH $starts_with AS starts_with
MATCH (t:Term)<-[r]-(c:Code)<-[:CODE]-(p:Concept)
WHERE r.CUI=p.CUI AND c.SAB='CL' AND TYPE(r) IN ['PT','SY']
// Allow for case-insensitive typeahead searches.
AND CASE WHEN starts_with = '' THEN 1=1 ELSE toLower(t.name) STARTS WITH starts_with END
RETURN COUNT(DISTINCT c.CodeID) as celltypelistcount
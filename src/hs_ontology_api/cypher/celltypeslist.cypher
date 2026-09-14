// Returns high-level information on cell types in the UBKG
// Used by the celltypes-info endpoint

WITH $starts_with AS starts_with
CALL
{
        WITH starts_with
        Optional MATCH (t:Term)<-[r]-(c:Code)<-[:CODE]-(p:Concept)
        WHERE r.CUI=p.CUI
        AND c.SAB='CL'
        AND TYPE(r) IN ['PT','SY']
        // Allow for case-insensitive typeahead searches.
        AND CASE WHEN starts_with = '' THEN 1=1 ELSE toLower(t.name) STARTS WITH starts_with END

        RETURN c.CodeID as id,
        p.CUI as CodeCUI
}
// Preferred terms
CALL
{
        WITH id
        OPTIONAL MATCH (c:Code)-[:PT]->(t:Term)
        WHERE c.CodeID=id
        RETURN DISTINCT t.name AS term
}
// Synoyms
CALL
{
        WITH id
        OPTIONAL MATCH (c:Code)-[:SY]->(t:Term)
        WHERE c.CodeID=id
        RETURN COLLECT(t.name) AS synonyms
}
// Definition
CALL
{
        WITH id
        OPTIONAL MATCH (t:Term)<-[r:PT]-(c:Code)<-[:CODE]-(p:Concept)-[:DEF]->(d:Definition)
        WHERE c.CodeID=id
        AND d.SAB = 'CL'
        AND r.CUI = p.CUI
        RETURN DISTINCT d.DEF AS definition
}
WITH id, term,synonyms,definition
// Pagination parameters to be added by calling function.
SKIP $skiprows
LIMIT $limitrows
WITH id, term, COLLECT(DISTINCT synonyms) AS synonyms,definition
ORDER BY id
RETURN {id:id, term:term, definition:definition,synonyms:synonyms} AS celltype


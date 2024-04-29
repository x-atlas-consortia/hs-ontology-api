// Returns high-level information on cell types in the UBKG
// Used by the celltypes-info endpoint

CALL
{
        Optional MATCH (t:Term)<-[r]-(c:Code)<-[:CODE]-(p:Concept)
        WHERE r.CUI=p.CUI
        AND c.SAB='CL'
        AND TYPE(r) IN ['PT','SY']
        // Allow for typeahead searches, but only on the preferred term provided by CL.
        // (Other ontologies can provide other preferred terms for a CL code; these have a PT_SAB relationship.)
        // The neo4j_logic will replace  starts_with_clause with a parameterized STARTS WITH clause.
        $starts_with_clause
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
RETURN DISTINCT id, term,synonyms,definition
ORDER BY id


 // Returns count of MGI genes in UBKG.
 // Case-insensitive typehead search on approved symbol (term type = SY)
 WITH $starts_with_clause AS starts_with_clause
 MATCH (tGene:Term)<-[:SY]-(cGene:Code)<-[:CODE]-(pGene:Concept)
  WHERE cGene.SAB='MGI'
 AND
  CASE
   WHEN starts_with_clause = '' THEN 1=1
   // Escape special characters.
    ELSE toUpper(replace(replace(replace(toString(tGene.name), "[", ""), "]", ""), "\'", ""))
    STARTS WITH toUpper(starts_with_clause)
  END
 RETURN COUNT(DISTINCT cGene) AS genelistcount

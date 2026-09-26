// Returns count of HGNC genes in UBKG.
// Case-insensitive typehead search on approved symbol (term type = ACR)
 WITH $starts_with_clause AS starts_with_clause
 MATCH (tGene:Term)<-[:ACR]-(cGene:Code)<-[:CODE]-(pGene:Concept)
  WHERE cGene.SAB='HGNC'
 AND
  CASE
   WHEN starts_with_clause = '' THEN 1=1
   ELSE toUpper(tGene.name) STARTS WITH toUpper(starts_with_clause)
  END
 RETURN COUNT(DISTINCT cGene) AS genelistcount

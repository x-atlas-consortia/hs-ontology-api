 // Returns count of MGI genes in UBKG.
 MATCH (tGene:Term)<-[:PT_HCOP]-(cGene:Code)<-[:CODE]-(pGene:Concept) WHERE cGene.SAB='MGI' $starts_with_clause RETURN COUNT(DISTINCT cGene) AS genelistcount

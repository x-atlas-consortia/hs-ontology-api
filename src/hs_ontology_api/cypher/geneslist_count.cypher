 // Returns count of HGNC genes in UBKG.
 MATCH (tGene:Term)<-[:ACR]-(cGene:Code)<-[:CODE]-(pGene:Concept) WHERE cGene.SAB='HGNC' $starts_with_clause RETURN COUNT(DISTINCT cGene) AS genelistcount

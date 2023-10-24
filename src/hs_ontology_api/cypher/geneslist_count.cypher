 // Returns count of HGNC genes with RefSeq definitions in UBKG.
 MATCH (cGene:Code)<-[:CODE]-(pGene:Concept) WHERE cGene.SAB='HGNC' RETURN COUNT(DISTINCT cGene) AS genelistcount

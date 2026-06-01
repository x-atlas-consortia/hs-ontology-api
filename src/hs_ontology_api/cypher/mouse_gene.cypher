// GENES
// Return reference information on a set of mouse genes, based on a input list of MGI identifiers.
// Used by the genes endpoint.

CALL

// Get CUIs of concepts for genes that match the criteria.

{

// Criteria: list of MGI identifiers.

// The following types of identifiers can be used in the list:
// 1. MGI numeric IDs (e.g., 2152878)
// 2. MGI approved symbols (e.g., A1bg)

// If no criteria are specified, return information on all MGI genes.

//WITH ['2152878','A1bg'] AS ids

// The calling function in neo4j_logic.py will replace $ids.
WITH [$ids] AS ids

// Find CUIs for genes that satisfy criteria for MGI ID or symbol.
// May 2026 Currently, HCOP gene symbols are lists of strings, for some reason.
// Parse the actual symbol.

OPTIONAL MATCH (pGene:Concept)-[:CODE]->(cGene:Code)-[r:SY]->(tGene:Term)
  WHERE r.CUI=pGene.CUI
  AND cGene.SAB='MGI'
  AND
  CASE
    WHEN ids[0]<>''
  THEN (ANY(id IN ids WHERE cGene.CODE=id)
  OR ANY(id in ids WHERE replace(replace(replace(tGene.name,"[",""),"]",""),"'","")=id))
    ELSE 1=1 END
RETURN DISTINCT pGene.CUI AS GeneCUI
}

CALL{

// Gene names and (parsed) symbols
WITH GeneCUI
OPTIONAL MATCH (pGene:Concept)-[:CODE]->(cGene:Code)-[r]->(tGene:Term)
  WHERE pGene.CUI=GeneCUI
  AND r.CUI=pGene.CUI
  AND type(r) IN ['PT_HCOP','SY']
  AND cGene.SAB='MGI'
RETURN toInteger(cGene.CODE) AS mgi_id,
       CASE type(r)
         WHEN 'PT_HCOP'
       THEN 'approved_name'
         WHEN 'SY'
       THEN 'approved_symbol'
         ELSE type(r)
         END AS ret_key,
       CASE type(r)
         WHEN 'PT_HCOP'
       THEN tGene.name
         ELSE replace(replace(replace(tGene.name,"[",""),"]",""),"'","")
         END AS ret_value
ORDER BY mgi_id, ret_key

UNION

// References to other vocabularies via 1:1 orthology (HCOP:HGNC)
WITH GeneCUI
OPTIONAL MATCH (cGene:Code)<-[:CODE]-(pGene:Concept)-[r:in_1_to_1_orthology_relationship_with]->(pRef:Concept)-[:CODE]->(cRef:Code)
  WHERE pGene.CUI=GeneCUI
  AND cGene.SAB='MGI'
RETURN
  toInteger(cGene.CODE) AS mgi_id,
  'references' AS ret_key,
  cRef.CodeID AS ret_value
ORDER BY mgi_id, ret_key

}

WITH mgi_id, ret_key, COLLECT(ret_value) AS values
WHERE mgi_id IS NOT NULL
WITH mgi_id,apoc.map.fromLists(COLLECT(ret_key),COLLECT(values)) AS map

// Add reference urls
WITH mgi_id, map,
        [ref IN map['references'] |
                {
                        id: split(ref,':')[1],
                        source: CASE split(ref,':')[0]
                                WHEN 'HGNC' THEN 'hugo'
                                ELSE toLower(split(ref,':')[0])
                        END,
                        url: CASE split(ref,':')[0]
                                WHEN 'UNIPROTKB' THEN 'https://www.uniprot.org/uniprot/' + split(ref,':')[1]
                                WHEN 'ENSEMBL' THEN 'https://www.ensembl.org/id/' + split(ref,':')[1]
                                WHEN 'OMIM' THEN 'https://omim.org/entry/' + split(ref,':')[1]
                                WHEN 'ENTREZ' THEN 'https://www.ncbi.nlm.nih.gov/gene/' + split(ref,':')[1]
                                WHEN 'HGNC' THEN 'https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/' + split(ref,':')[1]
                                ELSE ref
                        END
                }
        ] AS ref_objs

WITH mgi_id,
        {
            mgi_id:mgi_id,
                approved_name:map['approved_name'][0],
                approved_symbol:map['approved_symbol'][0],
                references:ref_objs
        } AS gene
WHERE mgi_id IS NOT NULL
RETURN COLLECT(gene) AS genes

// October 2025
// Returns information on cell type annotations.

// The calling function in neo4j_logic.py will replace variables preceded with $.

// Filter on SAB
WITH toUpper($sab) as sab
//WITH 'AZ' as sab
WITH sab,

// Optional filter on list of annotation codes or simple names
//['0000001','Arterial Endothelial'] AS ids
//WITH [''] AS ids

[$ids] AS ids

// Find all annotations that have the annotation parent and match the search terms.
MATCH (tAnn:Term)<-[rAnn:PT]-(cAnn:Code{SAB:sab})<-[:CODE]-(pAnn:Concept)-[:isa]->(pAnnParent:Concept)-[:CODE]->(cAnnParent:Code{CODE:'2000000'}),
(pAnn:Concept)-[:CODE]->(cCL:Code{SAB:'CL'})-[rCL:PT]->(tCL:Term)
WHERE rAnn.CUI=pAnn.CUI AND rCL.CUI=pAnn.CUI
AND (
        ids[0] <> '' AND
        ANY(id IN ids WHERE
            CASE
                WHEN id =~ '^\d+$' THEN
                    cAnn.SAB = sab
                    AND cAnn.CODE = id
                ELSE
                    toLower(tAnn.name) CONTAINS toLower(id)
            END
        )
        OR ids[0] = ''
    )

WITH sab, cAnn.CodeID AS Annotation_ID, tAnn.name AS Annotation_Fullname, split(tAnn.name,'_')[-1] AS Annotation_Name, cCL.CodeID AS CL_ID, tCL.name AS CL_Name ,pAnn.CUI AS Annotation_CUI
ORDER BY cAnn.CodeID

// Organ mapping
WITH sab, Annotation_ID, Annotation_Fullname, Annotation_Name, CL_ID, CL_Name, Annotation_CUI
MATCH (pAnn:Concept)-[rAnn:located_in]->(pOrgan:Concept)-[:CODE]->(cOrgan:Code)-[rOrgan]->(tOrgan:Term)
WHERE pAnn.CUI=Annotation_CUI
AND rOrgan.CUI=pOrgan.CUI
AND rAnn.SAB=sab
AND cOrgan.SAB=sab
AND TYPE(rOrgan) = 'PT'
AND Annotation_Fullname CONTAINS tOrgan.name

WITH sab, Annotation_ID, Annotation_Fullname, Annotation_Name, CL_ID, CL_Name,
cOrgan.SAB as OrganSAB, cOrgan.CodeID AS OrganCode, tOrgan.name AS OrganName
MATCH (tOrgSAB:Term)<-[rOrgSAB:PT]-(cOrgSAB:Code{CodeID:OrganCode})<-[:CODE]-(pU:Concept)-[:CODE]->(cU:Code{SAB:'UBERON'})-[rU:PT_UBERON_BASE]->(tU:Term)
WHERE rU.CUI=pU.CUI
AND rOrgSAB.CUI=pU.CUI

WITH sab, Annotation_ID, Annotation_Fullname, Annotation_Name,
{code: CL_ID, term: CL_Name} AS mapped_celltype,
{code:OrganCode, term: OrganName,uberon_code:cU.CodeID, uberon_term:tU.name} AS mapped_organ

WITH {code:Annotation_ID,
terms: {full: Annotation_Fullname, simple: Annotation_Name},
mapped_celltype: mapped_celltype,
mapped_organ: mapped_organ} AS celltype_annotation
RETURN COLLECT(DISTINCT celltype_annotation) AS annotations

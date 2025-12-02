// November 2025
// Returns information on the organ level codes of cell type annotations.

// Used by the annotations/organ-levels endpoints.

// The calling function in neo4j_logic.py will replace variables preceded with $.

// Optional filter on SAB
WITH toUpper($sab) as sab
//WITH 'VCCF' as sab
WITH sab,

// Optional filter on list of organ-level identifiers or search terms
//[''] AS ids
//['heart','100001'] AS ids
[$ids] AS ids

// Find all organ level codes (children of ID 1000000) that match the search terms.
// Find corresponding UBERON organ codes.
// Find annotations that are located in the organ level.

MATCH (cOLParent:Code{CODE:'1000000'})<-[:CODE]-(pOLParent:Concept)<-[:isa]-(pOL:Concept),
(tOL:Term)<-[rOL:PT]-(cOL:Code)<-[:CODE]-(pOL:Concept)-[:part_of]-(pUB:Concept)-[:CODE]->(cUB:Code)-[rUB:PT_UBERON_BASE]->(tUB:Term),
(pOL:Concept)<-[:located_in]-(pAnn:Concept)-[:CODE]-(cAnn:Code)-[rAnn:PT]-(tAnn:Term)
WHERE (
    (sab IS NOT NULL AND sab <> '' AND cOL.SAB = sab) OR
    ((sab IS NULL OR sab = '') AND cOL.SAB IN ['AZ','STELLAR','DCTH','PAZ','RIBCA','VCCF'])
)

// UBERON:0000082=mammalian kidney (mapped to same CUI as kidney)
// UBERON:0000170=pair of lungs (mapped to same CUI as lung)
AND NOT cUB.CodeID IN ['UBERON:0000082','UBERON:0000170']

AND rOL.CUI=pOL.CUI
AND rUB.CUI=pUB.CUI
AND cAnn.SAB=cOL.SAB
AND rAnn.CUI=pAnn.CUI
AND (
        ids[0] <> '' AND
        ANY(id IN ids WHERE
            CASE
                WHEN id =~ '^\d+$' THEN
                    (
                        (sab IS NOT NULL AND sab <> '' AND cOL.SAB = sab) OR
                        ((sab IS NULL OR sab = '') AND cOL.SAB IN ['AZ','STELLAR','DCTH','PAZ','RIBCA','VCCF'])
                    )
                    AND cOL.CODE = id
                ELSE
                    toLower(tOL.name) CONTAINS toLower(id)
            END
        )
        OR ids[0] = ''
    )


WITH pOL.CUI AS OLCUI, cOL.CodeID as OLID, tOL.name AS OLName, cUB.CodeID AS UBID, tUB.name AS UBName, pAnn.CUI AS AnnCUI,cAnn.CodeID AS AnnID, tAnn.name AS AnnName
ORDER BY AnnID, OLID, UBID

// Find CL codes that correspond to the annotation codes.
// Because multiple annotation codes cross-reference CL codes, the UBKG ETL's "preferred CUI" cross-referencing algorithm
// will link only a fraction of annotation codes to CL CUIs; the rest will be mapped to custom CUIs.
// To get all of the CL codes, go from annotation codes to CUIs to CL codes--
// not from annotation CUIs to CL codes.
OPTIONAL MATCH (cA:Code{CodeID:AnnID})<-[:CODE]-(pA:Concept)-[:CODE]->(cCL:Code{SAB:'CL'})-[rCL:PT]->(tCL:Term)
WHERE rCL.CUI=pA.CUI

WITH OLCUI, OLID, OLName, UBID, UBName, AnnID, AnnName,AnnCUI,cCL.CodeID AS CLID, tCL.name AS CLName
WITH OLCUI, OLID, OLName, UBID, UBName, AnnID, AnnName, COLLECT(DISTINCT{annotation_code:AnnID,annotation_term:AnnName, cl_code:CLID, cl_name:CLName}) AS annotations
RETURN COLLECT(DISTINCT{organ_level_code:OLID,organ_level_term:OLName,uberon_code:UBID,uberon_term:UBName,annotations:annotations}) AS organ_levels

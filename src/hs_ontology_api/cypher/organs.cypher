// JAS SEPT 2024 - Converted return to JSON. Added organ category and laterality.

//  Replaces and extends a read of the organ_types.yaml in the search-api. Used by endpoints in the organs route.

// The calling function in neo4j_logic.py will replace $sab.

// First, obtain CUIs for concepts associated with organs.
// These concepts are children of the concept for the C000008 code in the application ontology.
CALL
{
	MATCH (cParent:Code)<-[r1]-(pParent:Concept)<-[r2:isa]-(pOrgan:Concept)-[r3:CODE]->(cOrgan:Code)-[r4:PT]->(tOrgan:Term)
	WHERE cParent.SAB = $sab AND cParent.CODE = 'C000008' AND r2.SAB=$sab AND cOrgan.SAB=$sab AND r4.CUI=pOrgan.CUI
	RETURN cOrgan.CODE as OrganCode,cOrgan.SAB as OrganSAB,tOrgan.name as OrganName, pOrgan.CUI as OrganCUI
}
// Organ codes are cross-referenced to UBERON, where possible. Obtain the UBERON codes.
CALL
{
	WITH OrganCUI OPTIONAL MATCH (pOrgan:Concept)-[r1:CODE]->(cOrgan:Code)-[r2:PT]->(tOrgan:Term)
	WHERE pOrgan.CUI=OrganCUI AND cOrgan.SAB IN ['UBERON']
	AND r2.CUI=pOrgan.CUI RETURN cOrgan.CodeID AS OrganUBERON
}
// Obtain FMA codes.
CALL
{
	WITH OrganCUI OPTIONAL MATCH (pOrgan:Concept)-[r1:CODE]->(cOrgan:Code)-[r2:PT]->(tOrgan:Term)
	WHERE pOrgan.CUI=OrganCUI AND cOrgan.SAB IN ['FMA']
	AND r2.CUI=pOrgan.CUI RETURN CASE WHEN pOrgan.CUI= 'C0222601' THEN 'FMA:57991' WHEN pOrgan.CUI='C0222600' THEN 'FMA:57987' ELSE cOrgan.CodeID END AS OrganFMA
}
// RUI codes are property nodes linked to organ nodes.
CALL
{
	WITH OrganCUI OPTIONAL MATCH (pOrgan:Concept)-[r1:has_two_character_code]->(p2CC:Concept)-[r2:PREF_TERM]->(t2CC:Term)
	WHERE pOrgan.CUI=OrganCUI AND r1.SAB=$sab RETURN t2CC.name as OrganTwoCharacterCode
}
// Organ categories
CALL
{
   WITH OrganCUI
   OPTIONAL MATCH (pOrgan:Concept)-[:isa]-(pOrganCat:Concept)-[:isa]->(pCat:Concept)-[:CODE]->(cCat:Code),
   // HuBMAP name for the category
   (pOrganCat:Concept)-[:CODE]->(cOrganCat:Code)-[rOrganCat:PT]-(tOrganCat:Term),
   // UBERON code for the category
   (pOrganCat:Concept)-[:CODE]->(cUBERON:Code)
   WHERE pOrgan.CUI = OrganCUI
   //Organ cat parent
   AND cCat.SAB=$sab
   AND cCat.CODE='C045000'
   AND cOrganCat.SAB=$sab
   AND rOrganCat.CUI=pOrganCat.CUI
   AND cUBERON.SAB='UBERON'
   RETURN DISTINCT
   CASE
   // Kidney mapped to both kidney and mammalian kidney
   WHEN OrganCUI in ['C0227614','C0227613'] THEN 'UBERON:0002113'
   // Lung mapped to both lung and pair of lungs
   WHEN OrganCUI in ['C0225730','C0225706'] THEN 'UBERON:0002048'
   ELSE cUBERON.CodeID END AS OrganCatUBERON,tOrganCat.name AS OrganCatTerm
}
// Laterality
CALL
{
    WITH OrganCUI
    OPTIONAL MATCH (pOrgan:Concept)-[:has_laterality]->(pLaterality:Concept)-[:CODE]->(cLaterality:Code)-[rLaterality:PT]->(tLaterality:Term)
    WHERE pOrgan.CUI = OrganCUI
    AND rLaterality.CUI = pLaterality.CUI
    AND cLaterality.SAB=$sab
    // Return null for 'No Laterality' or 'Unknown Laterality'
    RETURN DISTINCT CASE WHEN cLaterality.CODE IN ['C030039','C030040','C030041','C030022','C030023'] THEN NULL ELSE REPLACE(tLaterality.name," Laterality","") END AS laterality
}
// Filter out the "Other" organ node.
WITH OrganCode,OrganSAB,OrganName,OrganTwoCharacterCode,OrganUBERON,OrganFMA,OrganCUI,laterality,
CASE WHEN OrganCatUBERON IS NULL THEN NULL ELSE {organ_uberon:OrganCatUBERON, term:OrganCatTerm} END AS category

WHERE NOT (OrganCode = 'C030071' AND OrganSAB=$sab)
RETURN DISTINCT {code:OrganCode, sab:OrganSAB, term:OrganName,
organ_uberon:CASE WHEN OrganUBERON IS NULL THEN OrganFMA ELSE OrganUBERON END,
rui_code:OrganTwoCharacterCode, organ_cui:OrganCUI, laterality:laterality, category:category} AS organ
ORDER BY organ.term
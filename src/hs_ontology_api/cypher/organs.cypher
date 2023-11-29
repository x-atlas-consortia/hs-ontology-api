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
	WHERE pOrgan.CUI=OrganCUI AND cOrgan.SAB='UBERON'
	AND r2.CUI=pOrgan.CUI RETURN cOrgan.CodeID AS OrganUBERON
}
// RUI codes are property nodes linked to organ nodes.
CALL
{
	WITH OrganCUI MATCH (pOrgan:Concept)-[r1:has_two_character_code]->(p2CC:Concept)-[r2:PREF_TERM]->(t2CC:Term)
	WHERE pOrgan.CUI=OrganCUI AND r1.SAB=$sab RETURN t2CC.name as OrganTwoCharacterCode
}
// Filter out the "Other" organ node.
WITH OrganCode,OrganSAB,OrganName,OrganTwoCharacterCode,OrganUBERON,OrganCUI
WHERE OrganCode <> 'C030071'
RETURN OrganCode,OrganSAB,OrganName,OrganUBERON,OrganTwoCharacterCode,OrganCUI ORDER BY OrganName

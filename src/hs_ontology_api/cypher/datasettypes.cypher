// Used by the dataset_types endpoint.

// Returns a set of dataset types--i.e., categories of assay classifications.

//Filter by application context.

WITH $context AS context

// Find the CUIs for all dataset types.
CALL
{
	MATCH (pType:Concept)-[:isa]->(pParent:Concept)
	WHERE pParent.CUI IN['HRAVS:1000361 CUI','HRAVS:1000362 CUI']
    RETURN pType.CUI as CUIType
 }
 // For each dataset type, determine whether it is active or inactive.
 // Filter on application context.
 CALL
 {
 	WITH CUIType,context
 	MATCH (tType:Term)<-[r:PT]-(cType:Code)<-[:CODE]-(pType:Concept)-[:isa]->(pAct:Concept)-[:CODE]->(cAct:Code)-[rAct:PT]->(tAct:Term)
 	WHERE pType.CUI=CUIType
 	AND cType.SAB=context
	AND cAct.SAB=context
 	AND r.CUI=pType.CUI
 	AND rAct.CUI = pAct.CUI
	AND CASE WHEN context='HUBMAP' THEN cAct.CODE IN ['C004030','C004031'] ELSE cAct.CODE IN ['C004022','C0040023'] END
 	RETURN DISTINCT cType.CodeID AS DatasetTypeCode, tType.name AS DatasetTypeTerm,tAct.name as DatasetTypeActive
 }
 //Filter on specified activity type (active or inactive).
 WITH CUIType, DatasetTypeCode, DatasetTypeTerm, DatasetTypeActive
 $filters
 WITH COLLECT(DISTINCT {code:DatasetTypeCode, name:DatasetTypeTerm, dataset_type_active:DatasetTypeActive}) AS datasettypes
 RETURN {dataset_types:datasettypes} AS response
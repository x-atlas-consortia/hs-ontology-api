// Called by the dataset-types endpoint.

// Filters:
// Application context
WITH '$context' AS context,
// Whether an EPIC (externally processed)
False AS epictype_filter

// Get dataset types.
CALL
{
        WITH context
        MATCH (tDatasetTypeParent:Term)<-[rDatasetTypeParent:PT {CUI:pDatasetTypeParent.CUI}]-(cDatasetTypeParent:Code {SAB:context})<-[:CODE]-(pDatasetTypeParent:Concept)<-[:isa]-(pDatasetType:Concept)-[:CODE]->(cDatasetType:Code {SAB:context})-[rDatasetType:PT {CUI:pDatasetType.CUI}]->(tDatasetType:Term)
        WHERE cDatasetTypeParent.CodeID = context + ':C003041'
        RETURN DISTINCT
                pDatasetType.CUI AS CUIDatasetType,
                cDatasetType.CODE AS CodeDatasetType,
                tDatasetType.name AS NameDatasetType
        ORDER BY tDatasetType.name
}

// Get assaytypes associated with dataset type.
CALL {
    WITH CUIDatasetType, context
    OPTIONAL MATCH (pDatasetType:Concept {CUI:CUIDatasetType})<-[:has_dataset_type]-
                   (pAssayClass:Concept)-[:CODE]->
                   (cAssayClass:Code {SAB:context})-[rAssayClass:PT {CUI:pAssayClass.CUI}]->
                   (tAssayClass:Term),
                   (pAssayClass:Concept)-[:has_assaytype]->
                   (pAssayType:Concept)-[:CODE]->
                   (cAssayType:Code {SAB:context})-[rAssayType:PT {CUI:pAssayType.CUI}]->
                   (tAssayType:Term)
    WITH cAssayType.CODE AS CodeAssayType, tAssayType.name AS NameAssayType
    WHERE CodeAssayType IS NOT NULL
    RETURN COLLECT(DISTINCT  NameAssayType) AS assaytypes
}

// Get whether an Epic datatype.
CALL {
    WITH CUIDatasetType, context
    OPTIONAL MATCH (pDatasetType:Concept {CUI:CUIDatasetType})-[:isa]->
                   (pEpic:Concept)-[:CODE]->
                   (cEpic:Code {SAB:context})
    WHERE cEpic.CODE = 'C004034'
    RETURN CASE WHEN COUNT(pEpic) > 0 THEN true ELSE false END AS is_externally_processed
}

WITH CodeDatasetType, NameDatasetType, assaytypes, is_externally_processed, context,
     CASE
       WHEN epictype_filter = 'true' THEN true
       WHEN epictype_filter = 'false' THEN false
       ELSE null
     END AS epictype_filter_bool
  WHERE (epictype_filter_bool IS NULL OR is_externally_processed = epictype_filter_bool)

// Stream response.
WITH {
        dataset_type:NameDatasetType,
        assaytypes:assaytypes,
        is_externally_processed:is_externally_processed
        } AS dataset_type
WITH DISTINCT dataset_type AS dataset_types
WHERE dataset_types IS NOT NULL
RETURN COLLECT(DISTINCT dataset_types) AS dataset_types
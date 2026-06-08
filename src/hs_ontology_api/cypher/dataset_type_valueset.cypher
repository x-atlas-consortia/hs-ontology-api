// Called by the dataset-types endpoint.

// Returns a valueset of dataset type codes.

WITH 'SENNET' AS context
// Get SenNet dataset types, defined as those associated with modalities.
CALL
{
        WITH context
        MATCH (tDatasetTypeParent:Term)<-[rDatasetTypeParent:PT {CUI:pDatasetTypeParent.CUI}]-(cDatasetTypeParent:Code {SAB:context})<-[:CODE]-(pDatasetTypeParent:Concept)<-[:isa]-(pDatasetType:Concept)-[:CODE]->(cDatasetType:Code {SAB:context})-[rDatasetType:PT {CUI:pDatasetType.CUI}]->(tDatasetType:Term),
              (pDatasetType:Concept)-[rModality:has_modality]->(pModality:Concept)
        WHERE cDatasetTypeParent.CODE = 'C003041'
        AND pModality IS NOT NULL

        RETURN DISTINCT
                pDatasetType.CUI AS CUIDatasetType,
                cDatasetType.CODE AS CodeDatasetType,
                tDatasetType.name AS NameDatasetType
        ORDER BY tDatasetType.name
}
WITH CodeDatasetType, NameDatasetType
RETURN DISTINCT {code:CodeDatasetType,name:NameDatasetType} AS dataset_types
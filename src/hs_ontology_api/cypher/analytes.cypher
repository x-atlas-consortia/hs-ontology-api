// Called by the analytes endpoint.

// Return information on analytes.

WITH 'SENNET' AS context,

// Debug filters.
//False AS epictype_filter,
//'' AS dataset_type_code,
//'C011902' AS dataset_type_code, // LC-MS,
//'' AS modality_code,
//'C046009' AS modality_code, // Proteomics
//'' AS analyte_code
//'C020131' AS analyte_code // protein

// Filters:
// Whether an EPIC (externally processed)
$epictype_filter AS epictype_filter,
// Dataset type code
$dataset_type_code AS dataset_type_code,
// Modality code
$modality_code AS modality_code,
// Analyte code
$analyte_code AS analyte_code


// Get analytes with optional filter on analyte code.

CALL
{
        WITH context, analyte_code
        MATCH (tAnalyteParent:Term)<-[rAnalyteParent:PT {CUI:pAnalyteParent.CUI}]-(cAnalyteParent:Code {SAB:context})<-[:CODE]-(pAnalyteParent:Concept)<-[:isa]-(pAnalyte:Concept)-[:CODE]->(cAnalyte:Code {SAB:context})-[rAnalyte:PT {CUI:pAnalyte.CUI}]->(tAnalyte:Term)
        WHERE cAnalyteParent.CODE='C002031'
        AND (analyte_code = '' OR cAnalyte.CODE = analyte_code)
        RETURN DISTINCT
                pAnalyte.CUI AS CUIAnalyte,
                cAnalyte.CODE AS CodeAnalyte,
                tAnalyte.name AS NameAnalyte
        ORDER BY tAnalyte.name
}

// Get modalities for analyte with optional modality code.
// Direction of relationship is (modality)-[has_analyte]->(analyte).
CALL
{
        WITH context, CUIAnalyte, modality_code
        MATCH (pAnalyte:Concept {CUI:CUIAnalyte})<-[:has_analyte]-(pModality:Concept)-[:CODE]->(cModality:Code {SAB:context})-[rModality:PT {CUI:pModality.CUI}]-(tModality:Term),(pModality:Concept)-[:isa]->(pModalityParent:Concept)-[:CODE]->(cModalityParent:Code {SAB:context})
        WHERE cModalityParent.CODE='C046000'
        AND (modality_code = '' OR cModality.CODE = modality_code)
        WITH pModality.CUI AS CUIModality, cModality.CODE AS CodeModality, split(tModality.name,'_modality')[0] AS NameModality
        WHERE CodeModality IS NOT NULL
        RETURN DISTINCT CUIModality, CodeModality, NameModality
}

// Get dataset types for modality with optional dataset_type code.
// Direction of relationship is (dataset_type)-[has_modality]->(modality).
CALL
{
        WITH context, CUIModality, dataset_type_code
        MATCH (pModality:Concept {CUI:CUIModality})<-[:has_modality]-(pDatasetType:Concept)-[:CODE]->(cDatasetType:Code {SAB:context})-[rDatasetType:PT {CUI:pDatasetType.CUI}]->(tDatasetType:Term),(pDatasetType:Concept)-[:isa]->(pDatasetTypeParent:Concept)-[:CODE]->(cDatasetTypeParent:Code{SAB:context})
        WHERE cDatasetTypeParent.CODE='C003041'
        AND (dataset_type_code='' OR cDatasetType.CODE=dataset_type_code)
        RETURN DISTINCT
          pDatasetType.CUI AS CUIDatasetType,
          cDatasetType.CODE AS CodeDatasetType,
          tDatasetType.name AS NameDatasetType
}

// Get whether an Epic datatype.
CALL
{
   WITH CUIDatasetType,context
   OPTIONAL MATCH (pDatasetType:Concept {CUI:CUIDatasetType})-[:isa]->(pEpic:Concept)-[:CODE]->(cEpic:Code {SAB:context})
   WHERE cEpic.CODE = 'C004034'
   RETURN DISTINCT CASE WHEN pEpic IS NULL THEN false ELSE true END AS is_externally_processed
}

// Get assaytypes associated with dataset type.
CALL
{
        WITH CUIDatasetType,context
        OPTIONAL MATCH (pDatasetType:Concept {CUI:CUIDatasetType})<-[:has_dataset_type]-(pAssayClass:Concept)-[:CODE]->(cAssayClass:Code {SAB:context})-[rAssayClass:PT {CUI:pAssayClass.CUI}]->(tAssayClass:Term),
        (pAssayClass:Concept)-[:has_assaytype]->(pAssayType:Concept)-[:CODE]-(cAssayType:Code {SAB:context})-[rAssayType:PT {CUI:pAssayType.CUI}]->(tAssayType:Term)
        WITH cAssayType.CODE AS CodeAssayType, tAssayType.name AS NameAssayType
        WHERE CodeAssayType IS NOT NULL
        RETURN COLLECT(DISTINCT {code:CodeAssayType,name:NameAssayType}) AS assaytypes
}

//Filter on epic type.

WITH CodeAnalyte,NameAnalyte,
     CodeModality,NameModality,
     CodeDatasetType,NameDatasetType,
     is_externally_processed,assaytypes,
     CASE
       WHEN epictype_filter = 'true' THEN true
       WHEN epictype_filter = 'false' THEN false
       ELSE null
     END AS epictype_filter_bool
WHERE CodeAnalyte IS NOT NULL
  AND (epictype_filter_bool IS NULL OR is_externally_processed = epictype_filter_bool)

// Stream response.
WITH CodeAnalyte,NameAnalyte,
     CodeModality,NameModality,
     COLLECT(DISTINCT {
        code:CodeDatasetType,
        name:NameDatasetType,
        is_externally_processed:is_externally_processed,
        assaytypes:assaytypes
     }) AS dataset_types
WHERE dataset_types <> []
WITH CodeAnalyte, NameAnalyte, {code:CodeModality, name:NameModality, dataset_types:dataset_types} AS modality
WITH CodeAnalyte, NameAnalyte, COLLECT(DISTINCT modality) AS modalities
WHERE modalities <> []
WITH {code:CodeAnalyte, name:NameAnalyte, modalities:modalities} AS analyte
WITH COLLECT(DISTINCT analyte) AS analytes
WHERE analytes <> []
RETURN {analytes:analytes} AS analytes
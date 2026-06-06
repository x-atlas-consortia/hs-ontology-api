// Called by the dataset-types endpoint.

// Return information on dataset types.
// Only return for the following cases:
// 1. All code filters are ''.
// 2. Each code filter corresponds to a valid code.


WITH 'SENNET' AS context,

// Debug filters.
//False AS epictype_filter,
//'' AS dataset_type_code,
//'C003076' AS dataset_type_code, // Visium (no probes),
//'' AS modality_code,
//'C046002' AS modality_code, // Microscopy
//'' AS analyte_code
//'C002045' AS analyte_code // collagen

// Filters:
// Application context
//WITH $context AS context,
// Whether an EPIC (externally processed)
$epictype_filter AS epictype_filter,
// Dataset type code
$dataset_type_code AS dataset_type_code,
// Modality code
$modality_code AS modality_code,
// Analyte code
$analyte_code AS analyte_code

// Get dataset types with optional filter on dataset type code.
CALL
{
        WITH context,dataset_type_code
        MATCH (tDatasetTypeParent:Term)<-[rDatasetTypeParent:PT {CUI:pDatasetTypeParent.CUI}]-(cDatasetTypeParent:Code {SAB:context})<-[:CODE]-(pDatasetTypeParent:Concept)<-[:isa]-(pDatasetType:Concept)-[:CODE]->(cDatasetType:Code {SAB:context})-[rDatasetType:PT {CUI:pDatasetType.CUI}]->(tDatasetType:Term)
        WHERE cDatasetTypeParent.CodeID = context + ':C003041'
        AND (dataset_type_code = '' OR cDatasetType.CODE = dataset_type_code)
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
    RETURN COLLECT(DISTINCT {code: CodeAssayType, name: NameAssayType}) AS assaytypes
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

// Get associated modalities and analytes with optional filters.
CALL {
    WITH CUIDatasetType, context, modality_code, analyte_code
    OPTIONAL MATCH
        (pDataSetType:Concept {CUI:CUIDatasetType})-[:has_modality]->
        (pModality:Concept)-[:isa]->
        (pModalityParent:Concept {CUI:'SENNET:C046000 CUI'}),
        (pModality:Concept)-[:CODE]->
        (cModality:Code {SAB:context})-[rModality:PT {CUI:pModality.CUI}]->
        (tModality:Term),
        (pModality:Concept)-[:has_analyte]->
        (pAnalyte:Concept)-[:CODE]->
        (cAnalyte:Code)-[rAnalyte:PT]->
        (tAnalyte:Term)
    WHERE (modality_code = '' OR cModality.CODE = modality_code)
      AND (analyte_code = '' OR cAnalyte.CODE = analyte_code)

    WITH DISTINCT
        cModality.CODE AS modality_code,
        split(tModality.name, '_modality')[0] AS modality_name,
        cAnalyte.CODE AS analyte_code,
        tAnalyte.name AS analyte_name
    WHERE modality_code IS NOT NULL
      AND analyte_code IS NOT NULL

    WITH modality_code, modality_name,
         COLLECT(DISTINCT {code: analyte_code, name: analyte_name}) AS analytes
    WHERE SIZE(analytes) > 0

    RETURN COLLECT({
        code: modality_code,
        name: modality_name,
        analytes: analytes
    }) AS modalities
}

WITH CodeDatasetType, NameDatasetType, modalities, assaytypes, is_externally_processed, context,
     CASE
       WHEN epictype_filter = 'true' THEN true
       WHEN epictype_filter = 'false' THEN false
       ELSE null
     END AS epictype_filter_bool
WHERE modalities <> []
  AND (epictype_filter_bool IS NULL OR is_externally_processed = epictype_filter_bool)

// Stream response.
WITH {
        dataset_type:{code:CodeDatasetType, name:NameDatasetType},
        modalities:modalities,
        assaytypes:assaytypes,
        is_externally_processed:is_externally_processed
        } AS dataset_type
WITH DISTINCT dataset_type AS dataset_types
WHERE dataset_types IS NOT NULL
RETURN {dataset_types:dataset_types} AS dataset_types
// Called by the modalities endpoint.

// Return information on modalities


WITH 'SENNET' AS context,

//False AS epictype_filter,
//'' AS dataset_type_code,
//'C011902' AS dataset_type_code, // LC-MS,
//'' AS modality_code,
//'C046009' AS modality_code, // Proteomics
//'' AS analyte_code
//'C020131' AS analyte_code // protein

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


// Get modalities with optional filter on modality code.
CALL {
    WITH context, modality_code
    MATCH (tModalityParent:Term)<-[rModalityParent:PT {CUI:pModalityParent.CUI}]-
          (cModalityParent:Code {SAB:context})<-[:CODE]-
          (pModalityParent:Concept)<-[:isa]-
          (pModality:Concept)-[:CODE]->
          (cModality:Code {SAB:context})-[rModality:PT {CUI:pModality.CUI}]->
          (tModality:Term)
    WHERE cModalityParent.CODE = 'C046000'
      AND (modality_code = '' OR cModality.CODE = modality_code)
    RETURN DISTINCT
        pModality.CUI AS CUIModality,
        cModality.CODE AS CodeModality,
        split(tModality.name, '_modality')[0] AS NameModality
    ORDER BY split(tModality.name, '_modality')[0]
}

// Get analytes with optional filter on analyte code.
CALL {
    WITH CUIModality, context, analyte_code
    MATCH (pModality:Concept {CUI:CUIModality})-[:has_analyte]->
          (pAnalyte:Concept)-[:CODE]->
          (cAnalyte:Code {SAB:context})-[rAnalyte:PT {CUI:pAnalyte.CUI}]->
          (tAnalyte:Term)
    WHERE analyte_code = '' OR cAnalyte.CODE = analyte_code
    WITH cAnalyte.CODE AS CodeAnalyte, tAnalyte.name AS NameAnalyte
    WHERE CodeAnalyte IS NOT NULL
    RETURN COLLECT(DISTINCT {code: CodeAnalyte, name: NameAnalyte}) AS analytes
}

// Get dataset types with optional filter on dataset type code.
CALL {
    WITH CUIModality, context, dataset_type_code
    MATCH (pModality:Concept {CUI:CUIModality})<-[:has_modality]-
          (pDatasetType:Concept)-[:CODE]->
          (cDatasetType:Code {SAB:context})-[rDataset:PT {CUI:pDatasetType.CUI}]->
          (tDatasetType:Term)
    WHERE dataset_type_code = '' OR cDatasetType.CODE = dataset_type_code
    RETURN DISTINCT
        pDatasetType.CUI AS CUIDatasetType,
        cDatasetType.CODE AS CodeDatasetType,
        tDatasetType.name AS NameDatasetType
    ORDER BY NameDatasetType
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

// Filter on epic type.
WITH CodeModality, NameModality, analytes, CodeDatasetType, NameDatasetType,
     is_externally_processed, assaytypes,
     CASE
       WHEN epictype_filter = 'true' THEN true
       WHEN epictype_filter = 'false' THEN false
       ELSE null
     END AS epictype_filter_bool
WHERE analytes <> []
  AND (epictype_filter_bool IS NULL OR is_externally_processed = epictype_filter_bool)

// Aggregate dataset types under modality.
WITH CodeModality, NameModality, analytes,
     COLLECT(DISTINCT {
       code: CodeDatasetType,
       name: NameDatasetType,
       is_externally_processed: is_externally_processed,
       assaytypes: assaytypes
     }) AS dataset_types
WHERE dataset_types <> []

WITH {code: CodeModality, name: NameModality, analytes: analytes, dataset_types: dataset_types} AS modality
WITH COLLECT(DISTINCT modality) AS modalities
WHERE modalities <> []
RETURN {modalities: modalities} AS modalities
// Called by the dataset-types endpoint.

// Return information on dataset types.


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
        WHERE cDatasetTypeParent.CodeID = context+':C003041'
        AND CASE
                WHEN dataset_type_code <> ''
                THEN cDatasetType.CODE=dataset_type_code
                ELSE 1=1 END

        RETURN DISTINCT
                pDatasetType.CUI AS CUIDatasetType,
                cDatasetType.CODE AS CodeDatasetType,
                tDatasetType.name AS NameDatasetType
        ORDER BY tDatasetType.name
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

// Get whether an Epic datatype.
CALL
{
   WITH CUIDatasetType,context
   OPTIONAL MATCH (pDatasetType:Concept {CUI:CUIDatasetType})-[:isa]->(pEpic:Concept)-[:CODE]->(cEpic:Code {SAB:context})
   WHERE cEpic.CODE = 'C004034'
   RETURN DISTINCT CASE WHEN pEpic IS NULL THEN false ELSE true END AS is_externally_processed
}

// Get modality and associated analytes with optional filters on modality code and analyte code.
CALL
{
    WITH CUIDatasetType,context,modality_code,analyte_code
    OPTIONAL MATCH
    (pDataSetType:Concept{CUI:CUIDatasetType})-[:has_modality]->(pModality:Concept)-[:isa]->(pModalityParent:Concept{CUI:'SENNET:C046000 CUI'}),
    (pModality:Concept)-[:CODE]->(cModality:Code{SAB:context})-[rModality:PT {CUI:pModality.CUI}]->(tModality:Term),
    (pModality:Concept)-[:has_analyte]->(pAnalyte:Concept)-[:CODE]->(cAnalyte:Code)-[rAnalyte:PT]->(tAnalyte:Term)
    WHERE CASE WHEN modality_code <> '' THEN cModality.CODE=modality_code ELSE 1=1 END
    AND CASE WHEN analyte_code <> '' THEN cAnalyte.CODE=analyte_code ELSE 1=1 END
    WITH DISTINCT
        cModality.CODE AS modality_code,
        split(tModality.name,'_modality')[0] AS modality_name,
        cAnalyte.CODE AS analyte_code,
        tAnalyte.name AS analyte_name
    WITH modality_code, modality_name, analyte_code, analyte_name
    WHERE modality_code IS NOT NULL
    AND analyte_code IS NOT NULL
    WITH modality_code, modality_name, COLLECT(DISTINCT {code:analyte_code, name:analyte_name}) AS analytes
    RETURN COLLECT({code:modality_code, name:modality_name, analytes:analytes}) AS modalities

}

// Filter on whether EPIC and modalities.
WITH CodeDatasetType, NameDatasetType, modalities, assaytypes, is_externally_processed, context
WHERE is_externally_processed=epictype_filter
and modalities <> []

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

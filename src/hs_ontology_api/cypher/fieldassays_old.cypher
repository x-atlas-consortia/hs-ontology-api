// Obtains associations between ingest metadata fields and assaytypes, both for legacy (HMFIELD) and CEDAR.
// Used by the field-assays endpoint.

// NOTE: With the deployment of the assay classifier (Rules Engine, or "soft assay types"), the UBKG is no longer the
// source of truth for assay type. This endpoint is primarily for legacy datasets.

// Identify all metadata fields, from both:
// - legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of HMFIELD:1000
// - current sources (CEDAR tempates, modeled in CEDAR), child codes of CEDAR:TemplateField
// Fields that are in the intersection of HMFIELD and CEDAR share CUIs.

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.

// The function that calls this query will replace the variable field_filter.
CALL
{
     MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT]->(tField:Term)
     WHERE rField.CUI=pField.CUI
     AND cFieldParent.CodeID IN ['HMFIELD:1000','CEDAR:TemplateField']
     $field_filter
     RETURN tField.name AS field_name, pField.CUI as CUIField, apoc.text.join(COLLECT(DISTINCT cField.CodeID),'|') AS code_ids
     ORDER BY tField.name
}

// For each field, find the associated assay identifier (originally from field_assays.yaml).
// These identifiers can be one of three types:
// - description
// - data_type
// - alt_name
// These identifiers are cross-referenced to CUIs for codes in the HUBMAP Dataset hierarchy.
//

// The function that calls this query will replace the variable assay_type_filter.
CALL
{
    WITH CUIField
    OPTIONAL MATCH (pField:Concept)-[:used_in_dataset]->(pAssay:Concept)-[:CODE]->(cAssay:Code)-[r:PT]->(tAssay:Term)
    WHERE pField.CUI=CUIField AND cAssay.SAB='HMFIELD'
    $assay_type_filter
    RETURN DISTINCT cAssay.CodeID AS assay_code_id,
    CASE WHEN tAssay.name IS NULL THEN 'none' ELSE tAssay.name END AS assay_identifier
}

// In HMFIELD, assay identifiers are cross-referenced to CUIs for codes in the HUBMAP "hard" Dataset hierarchy.
// Duplicate assignments are possible--e.g., a HuBMAP dataset is assigned to both a data_type and an alt-name.
// Because a CUI can be the "preferred" CUI for only one code in an ontology, this results in some assay identifiers
// being associated with multiple CUIs--i.e., one to the CUI shared by the HUBMAP dataset code,
// one to a new CUI for the HMFIELD code.
// We want the HUBMAP CUI for each HMFIELD code, regardless of whether it is the "preferred" CUI.

// SPECIAL CASE: The identifiers for 10x Multiome have so many variants of case and delimiter for
// 10x<delimiter>multiome, so hard-code the CUI mapping.

CALL
{
    WITH assay_code_id, assay_identifier
    OPTIONAL MATCH (pAssay:Concept)-[:CODE]->(cAssay:Code)
    WHERE cAssay.CodeID = assay_code_id
    AND pAssay.CUI STARTS WITH 'HUBMAP'
    RETURN distinct CASE WHEN assay_identifier='10x Multiome' THEN 'HUBMAP:C014002 CUI' ELSE pAssay.CUI END AS CUIHMDataset
}

// For each HuBMAP Dataset, obtain the data_type.

CALL
{
    WITH CUIHMDataset
    OPTIONAL MATCH (pAssay:Concept)-[:has_data_type]->(pDataType:Concept)-[:CODE]->(cDataType:Code)-[r:PT]->(tDataType:Term)
    WHERE pAssay.CUI=CUIHMDataset
    AND cDataType.SAB ='HUBMAP'
    AND r.CUI=pDataType.CUI
    RETURN CASE WHEN tDataType.name IS NULL THEN 'none' ELSE tDataType.name END AS data_type
}

// For each HuBMAP Dataset, obtain the "soft assay" dataset type.
// The "soft assay" dataset type is a member of the Soft Assay Dataset Type hierarchy in HUBMAP, with parent code
// HUBMAP:C003041
CALL
{
    WITH CUIHMDataset
    OPTIONAL MATCH (pAssay:Concept)-[:isa]->(pSoftAssayDatasetType:Concept)-[:isa]->(pSoftAssayDatasetTypeRoot:Concept)-[:CODE]->(cSoftAssayDatasetTypeRoot:Code)-[r:PT]->(tSoftAssayDatasetTypeRoot:Term),
    (pSoftAssayDatasetType:Concept)-[:CODE]->(cSoftAssayDatasetType:Code)-[r2:PT]->(tSoftAssayDatasetType:Term)
    WHERE pAssay.CUI = CUIHMDataset
    AND cSoftAssayDatasetTypeRoot.CodeID='HUBMAP:C003041'
    AND r.CUI=pSoftAssayDatasetTypeRoot.CUI
    AND r2.CUI=pSoftAssayDatasetType.CUI
    RETURN CASE WHEN tSoftAssayDatasetType.name IS NULL THEN 'none' ELSE tSoftAssayDatasetType.name END as dataset_type
}

// Collect assay_identifier, data_type, and dataset_type into a delimited list to flatten to level of field name.
// The function that calls this query will replace the variable data_type_dataset_type_filters.

WITH field_name, code_ids, assay_identifier, data_type, dataset_type
$data_type_dataset_type_filters
RETURN field_name, code_ids, COLLECT(DISTINCT assay_identifier + '|' + data_type + '|' + dataset_type) AS assays
ORDER BY field_name
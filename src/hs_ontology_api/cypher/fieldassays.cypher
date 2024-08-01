// Obtains associations between ingest metadata fields and assaytypes, for legacy metadata only (HMFIELD)
// Used by the field-assays endpoint.

// Identify all metadata fields, from legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of //HMFIELD:1000

// The function that calls this query will replace the variable field_filter.

CALL
{
     MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT]->(tField:Term)
     WHERE rField.CUI=pField.CUI
     AND cFieldParent.CodeID IN ['HMFIELD:1000']
     $field_filter
     RETURN tField.name AS field_name, pField.CUI as CUIField, cField.CodeID as field_code_id
     ORDER BY tField.name
}

// For each field, find the associated assay identifier (originally from field_assays.yaml).
// These identifiers can be one of three types:
// - description
// - assaytype
// - alt-name
// However, only assaytype is relevant: alt-names were deprecated, and descriptions are no longer current.

// The function that calls this query will replace the variable assay_type_filter.
// HMFIELD originally mapped fields to the "dataset type" in the older HuBMAP dataset hierarchy, but now maps directly to the HUBMAP
// code for the assaytype.
CALL
{
    WITH CUIField
    MATCH (pField:Concept)-[:used_in_dataset]->(pAssayType:Concept)-[:CODE]->(cAssayType:Code)-[r:PT]->(tAssayType:Term)
    WHERE pField.CUI=CUIField AND cAssayType.SAB='HUBMAP' AND r.CUI=pAssayType.CUI
    $assay_type_filter
    RETURN COLLECT(DISTINCT tAssayType.name) AS assaytypes
}
WITH field_name, assaytypes
WHERE assaytypes <>[]

RETURN {fields:COLLECT(DISTINCT {field_name: field_name, assaytypes:assaytypes})} AS fieldassays
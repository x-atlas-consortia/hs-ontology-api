// Obtains type associations for field names in legacy (HMFIELD) and CEDAR sources.
// Used by the field-types endpoint.

// Identify all metadata fields, from both:
// - legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of HMFIELD:1000
// - current sources (CEDAR tempates, modeled in CEDAR), child codes of CEDAR:TemplateField
// Fields that are in the intersection of HMFIELD and CEDAR share CUIs.

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.

// The field_types_get_logic in neo4j_logic will replace the field_filter variable.

CALL
{
     MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT]->(tField:Term)
     WHERE rField.CUI=pField.CUI
     AND cFieldParent.CodeID IN ['HMFIELD:1000','CEDAR:TemplateField']
     $field_filter
     RETURN tField.name AS field_name,
     apoc.text.join(COLLECT(DISTINCT cField.CodeID),'|') AS code_ids,
     pField.CUI AS CUIField
}

// For each field, find the data types associated with the field in both HMFIELD and CEDAR.
// 1. In general, a field in HMFIELD will have a different type than the equivalent in CEDAR.
// 2. Field cdes in HMFIELD are mapped to types in both HMFIELD and XSD.
// 3. Field codes in CEDAR are appropriately mapped to types in XSD.
// The preferred terms for the XSD type codes from CEDAR use PT_CEDAR.
// Collect type descriptions to flatten at the level of the field, in format
// <Source of mapping> | <Source of type> | type

// The mapping of CEDAR | HMFIELD | type is an artifact of a field being both in HMFIELD and CEDAR and will not be returned.

// The field_types_get_logic in neo4j_logic will replace the mapping_source_filter, type_source_filter, and type_filter variables.

// e.g., HMFIELD | XSD | xsd:string
CALL
{
     WITH CUIField
     OPTIONAL MATCH (pField:Concept)-[rdt:has_datatype]->(pType:Concept)-[:CODE]->(cType:Code)-[r]->(tType:Term)
     WHERE pField.CUI=CUIField
     AND TYPE(r) STARTS WITH 'PT'
     $mapping_source_filter
     $type_source_filter
     $type_filter
     AND NOT (rdt.SAB='CEDAR' AND cType.SAB='HMFIELD')
     RETURN COLLECT(DISTINCT rdt.SAB + '|' + cType.SAB + '|' + CASE WHEN tType.name CONTAINS ':' THEN split(tType.name,':')[1] ELSE tType.name END) AS types
}

WITH field_name, code_ids,types
WHERE types<>[]
RETURN field_name, code_ids,types

ORDER BY field_name
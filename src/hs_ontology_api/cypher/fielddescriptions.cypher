// Obtains descriptions for field names in legacy (HMFIELD) and CEDAR sources.
// Used by the field-descriptions endpoint.

// Identify all metadata fields, from both:
// - legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of HMFIELD:1000
// - current sources (CEDAR tempates, modeled in CEDAR), child codes of CEDAR:TemplateField
// Fields that are in the intersection of HMFIELD and CEDAR share CUIs.

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.
// Collect the HMFIELD and CEDAR definitions for each metadata field to flatten to level of field name.

// The function that calls this query will replace the variables field_filter and source_filter

MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT]->(tField:Term),
(pField:Concept)-[:DEF]->(d:Definition)
WHERE rField.CUI=pField.CUI
AND cFieldParent.CodeID IN ['HMFIELD:1000','CEDAR:TemplateField']
$field_filter
$source_filter
RETURN tField.name AS field_name, pField.CUI as CUIField,
COLLECT(DISTINCT d.SAB + '|' + d.DEF) AS defs, tField.name AS identifier, apoc.text.join(COLLECT(DISTINCT cField.CodeID),'|') AS code_ids
ORDER BY tField.name
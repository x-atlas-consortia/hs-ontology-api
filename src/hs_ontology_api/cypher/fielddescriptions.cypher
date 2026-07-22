// Obtains descriptions for field names in legacy (HMFIELD) and CEDAR sources.
// Used by the field-descriptions endpoint.

// Identify all metadata fields, from both:
// - legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of HMFIELD:1000
// - current sources (CEDAR tempates, modeled in CEDAR), child codes of CEDAR:TemplateField
// Fields that are in the intersection of HMFIELD and CEDAR share CUIs.

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.
// Collect the HMFIELD and CEDAR definitions for each metadata field to flatten to level of field name.

// The function that calls this query will replace the variables field_filter and source_filter

WITH $field_filter AS field_filter,
$source_filter AS source_filter

MATCH (cFieldParent:Code)<-[:CODE]-
(pFieldParent:Concept)-[:inverse_isa]->
(pField:Concept)-[:CODE]->
(cField:Code)-[rField:PT]->
(tField:Term),
(pField:Concept)-[:DEF]->(d:Definition)
WHERE rField.CUI=pField.CUI
AND cFieldParent.CodeID IN ['HMFIELD:1000','CEDAR:TemplateField']
AND CASE WHEN field_filter = "" THEN 1=1 ELSE tField.name=field_filter END
AND CASE
  WHEN source_filter = "" THEN d.SAB IN ['HMFIELD', 'CEDAR']
  WHEN source_filter IN ['HMFIELD', 'CEDAR'] THEN d.SAB = source_filter
  ELSE d.SAB = source_filter END
WITH tField.name as field_name,
COLLECT(DISTINCT cField.CodeID) AS code_ids,
COLLECT(DISTINCT {source: d.SAB, description:d.DEF}) AS descriptions
ORDER BY tField.name
RETURN COLLECT(DISTINCT {code_ids:code_ids,descriptions:descriptions,name:field_name}) AS code_ids

// Obtains associations between metadata fields and schemas (HMFIELD) or templates (CEDAR).
// Used by the field-schemas endpoint.

// Identify all metadata fields, from both:
// - legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of HMFIELD:1000
// - current sources (CEDAR tempates, modeled in CEDAR), child codes of CEDAR:TemplateField
// Fields that are in the intersection of HMFIELD and CEDAR share CUIs.

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.

// The field_schemas_get_logic in neo4j_logic will replace the field_filter variable.

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

// Get associated schemas.
// 1. Fields in HMFIELD have a _used_in_schema relationship with a node that corresponds to a HMFIELD schema;
// 2. Fields in CEDAR have an inverse_has_field relationship with a node that corresponds to a CEDAR template.

// The field_schemas_get_logic in neo4j_logic will replace the schema_filter variable.
CALL
{
     WITH CUIField
     OPTIONAL MATCH (pField:Concept)-[:used_in_schema]->(pSchema:Concept)-[:CODE]->(cSchema:Code)-[r:PT]->(tSchema:Term)
     WHERE pField.CUI=CUIField and r.CUI=pSchema.CUI
     AND cSchema.SAB='HMFIELD'
     $schema_filter
     RETURN DISTINCT 'HMFIELD|' + tSchema.name as schema_name

     UNION
     WITH CUIField
     OPTIONAL MATCH (pField:Concept)<-[:has_field]-(pTemplate:Concept)-[:CODE]->(cTemplate:Code)-[r:PT]->(tSchema:Term)
     WHERE pField.CUI=CUIField and r.CUI=pTemplate.CUI
     $schema_filter
     AND cTemplate.SAB='CEDAR'
     RETURN DISTINCT 'CEDAR|' + tSchema.name as schema_name
}

// The field_schemas_get_logic in neo4j_logic will replace the mapping_source_filter variable.
WITH field_name, code_ids, schema_name
WHERE schema_name<>[]
$mapping_source_filter
RETURN field_name, code_ids, COLLECT (DISTINCT schema_name) AS schemas
ORDER BY field_name
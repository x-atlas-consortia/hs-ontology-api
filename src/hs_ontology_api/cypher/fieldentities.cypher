// Obtains entities associated with fields.
// Replaces field_entities.yaml.

// The query result has the following format for the entities column:
// HMFIELD|<Code in HMFIELD>|<term in HMFIELD>;HUBMAP|<Code in HUBMAP>|<term in HUMBMAP>, etc.
// i.e.,
// 1. The comma delimits the entities associated with a field.
// 2. The semicolon delimits the entities by ontology (i.e., HMFIELD or HUBMAP).
// 3. The pipe delimits the properties for an entity in an ontology for an entity.
// example for a field that maps to both the "sample" and "dataset" entities.
// ["HMFIELD|3004|sample;HUBMAP|C040002|Sample", "HMFIELD|3001|dataset;HUBMAP|C040001|Dataset"]

/// Identify all metadata fields, from both:
// - legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of HMFIELD:1000
// - current sources (CEDAR tempates, modeled in CEDAR), child codes of CEDAR:TemplateField
// Fields that are in the intersection of HMFIELD and CEDAR share CUIs.

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.

// The field_entities_get_logic in neo4j_logic will replace the field_filter and source_filter variables.

WITH $source_filter AS source_filter
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
// For each field, get associated entities from HMFIELD and HUBMAP ontologies.
// Each HMFIELD entity node is cross-referenced to a HUBMAP entity node.
// (CEDAR fields are currently not associated with entities.)
// The field_entities_get_logic in neo4j_logic will replace the entity_filter and source_filter variables.
CALL
{
     WITH CUIField, source_filter
     OPTIONAL MATCH (pField:Concept)-[:used_in_entity]->(pEntity:Concept)-[:CODE]->(cHMFIELDEntity:Code)-[rHMFIELD:PT]->(tHMFIELDEntity:Term),
     (pEntity:Concept)-[:CODE]->(cHUBMAPEntity:Code)-[rHUBMAP:PT]->(tHUBMAPEntity:Term)
     WHERE pField.CUI=CUIField AND cHMFIELDEntity.SAB ='HMFIELD' AND rHMFIELD.CUI=pEntity.CUI
     AND cHUBMAPEntity.SAB='HUBMAP' AND rHUBMAP.CUI=pEntity.CUI
     $entity_filter
     RETURN apoc.text.join([CASE WHEN source_filter in ['HMFIELD',''] THEN REPLACE(cHMFIELDEntity.CodeID,':','|') + '|' + tHMFIELDEntity.name ELSE '' END,
     CASE WHEN source_filter in ['HUBMAP',''] THEN REPLACE(cHUBMAPEntity.CodeID,':','|') + '|' + tHUBMAPEntity.name ELSE '' END],';') AS entity

}

WITH field_name, code_ids, COLLECT(entity) AS entities
WHERE entities <>['null;null']
RETURN field_name, code_ids, entities
ORDER BY field_name

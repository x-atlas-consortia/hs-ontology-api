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

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.

// The field_entities_get_logic in neo4j_logic will replace variables that start with the dollar sign.

// source_filter allows filtering by mapping source (HMFIELD or CEDAR).
// field_filter allows filtering by field name.

WITH $source_filter AS source_filter,
$field_filter AS field_filter,
$entity_filter AS entity_filter,
$application_filter AS application_filter
CALL
{
     MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT {CUI:pField.CUI}]->(tField:Term)
     WHERE cFieldParent.CodeID IN ['HMFIELD:1000','CEDAR:TemplateField']
     AND CASE WHEN field_filter = "" THEN 1=1 ELSE tField.name=field_filter END
     //$field_filter
     RETURN tField.name AS field_name,
     apoc.text.join(COLLECT(DISTINCT cField.CodeID),'|') AS code_ids,
     pField.CUI AS CUIField
}
// For each field, get associated provenance entities.
// entity_filter allows filtering for provenance entity by name--e.g., "dataset", "Dataset".
// application_filter allows filtering on application context--i.e., "HUBMAP" or "SENNET".

CALL
{
    // Each HMFIELD field node is linked to a HMFIELD entity node.
    WITH CUIField,source_filter, entity_filter, application_filter
    OPTIONAL MATCH
      (pField:Concept {CUI:CUIField})-[:used_in_entity]->
      (pEntity:Concept)-[:CODE]->(cEntity:Code)-[r:PT {CUI:pEntity.CUI}]->
      (tEntity:Term)
    WHERE cEntity.SAB ='HMFIELD'
    //$entity_filter
    AND CASE WHEN entity_filter= "" THEN 1=1 ELSE tEntity.name=entity_filter END
    RETURN DISTINCT CASE WHEN source_filter IN ['HMFIELD',''] THEN REPLACE(cEntity.CodeID,':','|') + '|' + tEntity.name ELSE '' END AS entity

    UNION

    // Each HMFIELD entity node is cross-referenced to HUBMAP and SENNET provenance entity nodes.
    WITH CUIField,source_filter, entity_filter, application_filter
    OPTIONAL MATCH
      (pField:Concept {CUI:CUIField})-[:used_in_entity]->
      (pEntity:Concept)-[:CODE]->(cEntity:Code)-[r:PT{CUI:pEntity.CUI}]->
      (tEntity:Term)
    //$application_filter
    WHERE CASE WHEN application_filter = "" THEN 1=1 ELSE cEntity.SAB IN [application_filter] END
    //$entity_filter
    AND CASE WHEN entity_filter= "" THEN 1=1 ELSE tEntity.name=entity_filter END
    RETURN DISTINCT CASE WHEN source_filter IN ['HMFIELD',''] THEN REPLACE(cEntity.CodeID,':','|') + '|' + tEntity.name ELSE '' END AS entity

    UNION

    //CEDAR template nodes are mapped to provenance entity nodes in both HUBMAP and SENNET.
    //CEDAR field nodes relate to CEDAR template nodes.

    WITH CUIField,source_filter, entity_filter, application_filter
    OPTIONAL MATCH
      (pField:Concept {CUI:CUIField})-[:inverse_has_field]->
      (pTemplate:Concept)-[:used_in_entity]->(pEntity:Concept)-[:CODE]->
      (cEntity:Code)-[r:PT{CUI:pEntity.CUI}]->(tEntity:Term)
    //$application_filter
        WHERE CASE WHEN application_filter = "" THEN 1=1 ELSE cEntity.SAB IN [application_filter] END
    //$entity_filter
      AND CASE WHEN entity_filter= "" THEN 1=1 ELSE tEntity.name=entity_filter END
    RETURN DISTINCT CASE WHEN source_filter IN ['CEDAR',''] THEN REPLACE(cEntity.CodeID,':','|') + '|' + tEntity.name ELSE '' END AS entity
}

WITH field_name, code_ids, entity
WHERE entity <>""
WITH field_name, code_ids, COLLECT(entity) AS entities
RETURN field_name, code_ids, entities
ORDER BY field_name

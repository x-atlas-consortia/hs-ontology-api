// Obtains entities associated with fields.
// Replaces field_entities.yaml.
// HMFIELD represents field mappings prior to the deployment of the CEDAR metadata manager.

// Optional filters:
// $mapping_source_filter - filter on mapping source (HMFIELD or CEDAR)
WITH $source_filter AS source_filter,

// $field_filter - name of field on which to filter
$field_filter AS field_filter,

// $entity_filter - name of entity on which to filter
$entity_filter AS entity_filter,

// $application_filter - name of application context (HUBMAP or SENNET)
$application_filter AS application_filter

// First, find identifiers for fields. Fields are defined in both HMFIELD and CEDAR hierarchies.

WITH
  source_filter,
  field_filter,
  entity_filter,
  application_filter
MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->
(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT {CUI:pField.CUI}]->(tField:Term)
WHERE cFieldParent.CodeID IN ['HMFIELD:1000','CEDAR:TemplateField']
AND CASE WHEN field_filter = "" THEN 1=1 ELSE tField.name=field_filter END

// For each field, get associated provenance entities.
// entity_filter allows filtering for provenance entity by name--e.g., "dataset", "Dataset".
// application_filter allows filtering on application context--i.e., "HUBMAP" or "SENNET".

WITH
  source_filter,
  entity_filter,
  application_filter,
  tField.name AS field_name,
  COLLECT(DISTINCT cField.CodeID) AS field_code_ids,
  pField.CUI AS CUIField
  ORDER BY tField.name

CALL
{
    // 1. Each HMFIELD field node is linked to a HMFIELD entity node.
    // For UNION symmetry, filter to the HMFIELD source.
    WITH
      CUIField,
      source_filter,
      entity_filter,
      application_filter,
      field_name,
      field_code_ids

    MATCH
      (pField:Concept {CUI:CUIField})-[:used_in_entity]->
      (pEntity:Concept)-[:CODE]->(cEntity:Code)-[r:PT {CUI:pEntity.CUI}]->
      (tEntity:Term)
    WHERE cEntity.SAB ='HMFIELD'
    AND CASE
      WHEN entity_filter= ""
      THEN 1=1
      ELSE tEntity.name=entity_filter
    END
    RETURN
      {code:cEntity.CodeID,
      name:tEntity.name,
      source:'HMFIELD'} AS entity

    UNION

    //2. Each HMFIELD entity node is cross-referenced to HUBMAP and SENNET provenance entity nodes.

    WITH
      CUIField,
      source_filter,
      entity_filter,
      application_filter,
      field_name,
      field_code_ids

    MATCH
      (pField:Concept {CUI:CUIField})-[:used_in_entity]->
      (pEntity:Concept)-[:CODE]->(cEntity:Code)-[r:PT {CUI:pEntity.CUI}]->
      (tEntity:Term)
    WHERE CASE
      WHEN application_filter = ""
      THEN cEntity.SAB in ['HUBMAP','SENNET']
      ELSE cEntity.SAB IN [application_filter]
    END
    AND CASE
      WHEN entity_filter= ""
      THEN 1=1
      ELSE tEntity.name=entity_filter
    END
    RETURN
      {code:cEntity.CodeID,
      name:tEntity.name,
      source:'HMFIELD'} AS entity

    UNION

    //3. CEDAR template nodes are mapped to provenance entity nodes in both HUBMAP and SENNET.
    //   CEDAR field nodes relate to CEDAR template nodes.

    WITH
      CUIField,
      source_filter,
      entity_filter,
      application_filter,
      field_name,
      field_code_ids

    MATCH
      (pField:Concept {CUI:CUIField})-[:inverse_has_field]->
      (pTemplate:Concept)-[:used_in_entity]->(pEntity:Concept)-[:CODE]->
      (cEntity:Code)-[r:PT{CUI:pEntity.CUI}]->(tEntity:Term)
    WHERE
      CASE
        WHEN application_filter = ""
        THEN cEntity.SAB IN ['HUBMAP','SENNET']
        ELSE cEntity.SAB IN [application_filter]
    END
    AND
      CASE
        WHEN entity_filter= ""
        THEN 1=1
        ELSE tEntity.name=entity_filter
      END
    RETURN
      {code:cEntity.CodeID,
      name:tEntity.name,
      source:'CEDAR'} AS entity
}

WITH field_name, field_code_ids, COLLECT(entity) as entities
RETURN {name:field_name, code_ids:field_code_ids, entities:{nodes:entities}} AS field_entity
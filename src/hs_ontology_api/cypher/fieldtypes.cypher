// Identify all metadata fields, from both:
// - legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of HMFIELD:1000
// - current sources (CEDAR tempates, modeled in CEDAR), child codes of CEDAR:TemplateField
// Fields that are in the intersection of HMFIELD and CEDAR share CUIs.

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.

CALL
{
     MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT]->(tField:Term)
     WHERE rField.CUI=pField.CUI
     AND cFieldParent.CodeID IN ['HMFIELD:1000','CEDAR:TemplateField']
     RETURN tField.name AS field_name, 
     apoc.text.join(COLLECT(DISTINCT cField.CodeID),'|') AS code_ids, 
     pField.CUI AS CUIField
}

// For each field, find all data types associated with the field. In general, a field in HMFIELD will have a different
// type than equivalent in CEDAR.
// The preferred terms for the XSD type codes from CEDAR use PT_CEDAR.
// Collect type descriptions to flatten at the level of the field.
CALL
{
     WITH CUIField
     OPTIONAL MATCH (pField:Concept)-[:has_datatype]->(pType:Concept)-[:CODE]->(cType:Code)-[r]->(tType:Term)
     WHERE pField.CUI=CUIField 
     AND TYPE(r) STARTS WITH 'PT'
     RETURN COLLECT(DISTINCT cType.SAB + '|' + tType.name) AS types
}

WITH field_name, code_ids,types
RETURN field_name, code_ids,types

ORDER BY field_name
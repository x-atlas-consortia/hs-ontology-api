// Obtains type associations for field names in legacy (HMFIELD) and CEDAR sources.
// Used by the field-types endpoint.

// Optional filters:
// field name
WITH $field_filter AS field_filter,
// mapping source
$mapping_source_filter AS mapping_source_filter,
// type source
$type_source_filter AS type_source_filter,
// type
$type_filter AS type_filter

// Identify all metadata fields, from both:
// - legacy sources (the field_*.yaml files in ingest-validation-tools, and modeled in HMFIELD), child codes of HMFIELD:1000
// - current sources (CEDAR tempates, modeled in CEDAR), child codes of CEDAR:TemplateField
// Fields that are in the intersection of HMFIELD and CEDAR share CUIs.

// Collect the HMFIELD and CEDAR codes for each metadata field to flatten to level of field name.
WITH
     field_filter,
     mapping_source_filter,
     type_source_filter,
     type_filter
MATCH
     (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->
     (pField:Concept)-[:CODE]->(cField:Code)-[rField:PT{CUI:pField.CUI}]->(tField:Term)
WHERE
     cFieldParent.CodeID IN ['HMFIELD:1000','CEDAR:TemplateField']
AND CASE
     WHEN field_filter = '' THEN 1=1
     ELSE tField.name=field_filter END
AND cField.SAB IN ['HMFIELD', 'CEDAR']


// For each field, find the data types associated with the field in both HMFIELD and CEDAR.
// 1. In general, a field in HMFIELD will have a different type than the equivalent in CEDAR.
// 2. Field cdes in HMFIELD are mapped to types in both HMFIELD and XSD.
// 3. Field codes in CEDAR are appropriately mapped to types in XSD.
// The preferred terms for the XSD type codes from CEDAR use PT_CEDAR.
// Collect type descriptions to flatten at the level of the field, in format
// <Source of mapping> | <Source of type> | type

// The mapping of CEDAR | HMFIELD | type is an artifact of a field being both in HMFIELD and CEDAR and will not be returned.

// e.g., HMFIELD | XSD | xsd:string

WITH
     mapping_source_filter,
     type_source_filter,
     type_filter,
     tField.name AS field_name,
     COLLECT(DISTINCT cField.CodeID) AS code_ids,
     pField.CUI AS CUIField

OPTIONAL MATCH
     (pField:Concept{CUI:CUIField})-[rdt:has_datatype]->(pType:Concept)-
     [:CODE]->(cType:Code)-[r{CUI:pType.CUI}]->(tType:Term)
WHERE TYPE(r) STARTS WITH 'PT'
AND rdt.SAB IN mapping_source_filter
AND cType.SAB IN type_source_filter
AND CASE
     WHEN type_filter='' THEN 1=1
     ELSE
          CASE WHEN tType.name CONTAINS ':'
               THEN split(tType.name,':')[1] = type_filter
               ELSE tType.name = type_filter END
     END
AND NOT (rdt.SAB='CEDAR' AND cType.SAB='HMFIELD')

WITH
     field_name,
     code_ids,
     rdt.SAB AS mapping_source,
     cType.SAB AS type_source,
     CASE WHEN
          tType.name CONTAINS ':' THEN split(tType.name,':')[1]
          ELSE tType.name END
     AS field_type
WHERE field_type IS NOT NULL

WITH
     field_name,
     code_ids,
     COLLECT(DISTINCT {mapping_source:mapping_source, type_source:type_source, type:field_type}) AS types

RETURN DISTINCT {code_ids:code_ids,name:field_name,types:types} AS field_types

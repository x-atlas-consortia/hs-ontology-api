// Returns a unique list of types in one of the type ontologies (HMFIELD or XSD).
// Used by the field-types endpoint.

WITH $type_source_filter AS type_source_filter

MATCH (cParentType:Code)<-[:CODE]-(pParentType:Concept)<-[:isa]-
(pType:Concept)-[:CODE]->(cType:Code)-[r]->(tType:Term)
WHERE cParentType.CodeID IN ['XSD:anySimpleType','HMFIELD:2000']
AND cType.SAB IN type_source_filter

WITH cType.SAB AS type_source,
CASE
  WHEN tType.name CONTAINS ':' THEN split(tType.name,':')[1]
  ELSE tType.name
  END AS type_name

WITH  {type:type_name,type_source:type_source} AS field_types

RETURN DISTINCT field_types
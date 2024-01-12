// Returns a unique list of types in one of the type ontologies (HMFIELD or XSD).
// Used by the field-types endpoint.

// The field_types_list_get_logic function replaces the values of mapping_source_filter and type_source_filter.

MATCH (cParentType:Code)<-[:CODE]-(pParentType:Concept)<-[:isa]-(pType:Concept)-[:CODE]->(cType:Code)-[r]->(tType:Term)
WHERE cParentType.CodeID IN ['XSD:anySimpleType','HMFIELD:2000']
$type_source_filter
RETURN DISTINCT  cType.SAB + '|' + CASE WHEN tType.name CONTAINS ':' THEN split(tType.name,':')[1] ELSE tType.name END AS type
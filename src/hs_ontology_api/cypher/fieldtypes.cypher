// GET HMFIELD Field-type information
CALL
{OPTIONAL MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT]->(tField:Term) WHERE rField.CUI=pField.CUI AND cFieldParent.CodeID='HMFIELD:1000' AND cField.SAB = 'HMFIELD' RETURN DISTINCT cField.CodeID AS FieldCodeID, tField.name AS FieldName, pField.CUI as CUIField}
CALL
{WITH CUIField
OPTIONAL MATCH (pField:Concept)-[:has_datatype]->(pType:Concept)-[:CODE]->(cType:Code)-[r:PT]->(tType:Term)
WHERE pField.CUI=CUIField AND cType.SAB='HMFIELD' AND r.CUI=pType.CUI
RETURN cType.CodeID AS TypeCodeID, tType.name as TypeName, pType.CUI AS CUIType
}
WITH FieldCodeID, FieldName, TypeCodeID, TypeName, CUIType
OPTIONAL MATCH (pType:Concept)-[:CODE]->(cType:Code)-[r:PT_CEDAR]->(tType:Term)
WHERE pType.CUI=CUIType AND cType.SAB='XSD' AND r.CUI=pType.CUI
RETURN FieldCodeID, FieldName, TypeCodeID, TypeName, cType.CodeID AS xrefTypeCodeID, tType.name AS xrefTypeCodeName
ORDER BY FieldCodeID
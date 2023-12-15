//GET HMFIELD Field information
MATCH (cFieldParent:Code)<-[:CODE]-(pFieldParent:Concept)-[:inverse_isa]->(pField:Concept)-[:CODE]->(cField:Code)-[rField:PT]->(tField:Term),
(pField:Concept)-[:DEF]->(dField:Definition)
WHERE rField.CUI=pField.CUI
AND cFieldParent.CodeID='HMFIELD:1000'
AND cField.SAB = 'HMFIELD'
AND dField.SAB='HMFIELD'
RETURN DISTINCT cField.CodeID AS codeID,
tField.name AS identifier,
dField.DEF AS description
ORDER BY identifier
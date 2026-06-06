// Called by the modalities endpoint.

// Return a simple valueset of information on modalities.

WITH 'SENNET' AS context

// Get modalities with optional filter on modality code.
CALL
{
        WITH context
        MATCH (tModalityParent:Term)<-[rModalityParent:PT {CUI:pModalityParent.CUI}]-(cModalityParent:Code {SAB:context})<-[:CODE]-(pModalityParent:Concept)<-[:isa]-(pModality:Concept)-[:CODE]->(cModality:Code {SAB:context})-[rModality:PT {CUI:pModality.CUI}]->(tModality:Term)
        WHERE cModalityParent.CODE='C046000'
        RETURN DISTINCT
                pModality.CUI AS CUIModality,
                cModality.CODE AS CodeModality,
                split(tModality.name,'_modality')[0] AS NameModality
        ORDER BY split(tModality.name,'_modality')[0]
}
WITH CUIModality, CodeModality, NameModality
WITH {code:CodeModality,name:NameModality} AS modality
RETURN DISTINCT modality AS modalities

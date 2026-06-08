// Called by the analytes endpoint.

// Return information on analytes.

WITH 'SENNET' AS context

CALL
{
        WITH context
        MATCH (tAnalyteParent:Term)<-[rAnalyteParent:PT {CUI:pAnalyteParent.CUI}]-(cAnalyteParent:Code {SAB:context})<-[:CODE]-(pAnalyteParent:Concept)<-[:isa]-(pAnalyte:Concept)-[:CODE]->(cAnalyte:Code {SAB:context})-[rAnalyte:PT {CUI:pAnalyte.CUI}]->(tAnalyte:Term)
        WHERE cAnalyteParent.CODE='C002031'
        RETURN DISTINCT
                pAnalyte.CUI AS CUIAnalyte,
                cAnalyte.CODE AS CodeAnalyte,
                tAnalyte.name AS NameAnalyte
        ORDER BY tAnalyte.name
}

WITH CodeAnalyte, NameAnalyte
RETURN DISTINCT {code:CodeAnalyte,name:NameAnalyte} AS analytes

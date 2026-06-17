// Called by the dataset-types endpoint.

// Filters:
// Application context
WITH '$context' AS context,
// Whether an EPIC (externally processed)
false AS epictype_filter

// Get dataset types.
CALL
{
        WITH context
        MATCH (tDatasetTypeParent:Term)<-[rDatasetTypeParent:PT {CUI:pDatasetTypeParent.CUI}]-(cDatasetTypeParent:Code {SAB:context})<-[:CODE]-(pDatasetTypeParent:Concept)<-[:isa]-(pDatasetType:Concept)-[:CODE]->(cDatasetType:Code {SAB:context})-[rDatasetType:PT {CUI:pDatasetType.CUI}]->(tDatasetType:Term)
        WHERE cDatasetTypeParent.CodeID = context + ':C003041'
        RETURN DISTINCT
                pDatasetType.CUI AS CUIDatasetType,
                cDatasetType.CODE AS CodeDatasetType,
                tDatasetType.name AS NameDatasetType
        ORDER BY tDatasetType.name
}
// Pipeline Decision Rules category
CALL
{
        WITH CUIDatasetType,context
        OPTIONAL MATCH (pDatasetType:Concept)-[:has_pdr_category]->(pPDRCategory:Concept)-[:CODE]->(cPDRCategory:Code)-[r:PT]->(tPDRCategory:Term)
        WHERE pDatasetType.CUI=CUIDatasetType AND r.CUI=pPDRCategory.CUI AND cPDRCategory.SAB=context
        RETURN DISTINCT tPDRCategory.name AS pdr_category
}
// Fig 2 aggregated assay type
CALL
{
        WITH CUIDatasetType,context
        OPTIONAL MATCH (pDatasetType:Concept)-[:has_fig2_agg_assay_type]->(pFig2agg:Concept)-[:CODE]-(cFig2agg:Code)-[r:PT]->(tFig2agg:Term)
        WHERE pDatasetType.CUI=CUIDatasetType AND r.CUI=pFig2agg.CUI AND cFig2agg.SAB=context
        RETURN DISTINCT tFig2agg.name AS fig2_aggregated_assaytype
}
// Fig2 modality
CALL
{
        WITH CUIDatasetType,context
        OPTIONAL MATCH (pDatasetType:Concept)-[:has_fig2_modality]->(pFig2modality:Concept)-[:CODE]-(cFig2modality:Code)-[r:PT]->(tFig2modality:Term)
        WHERE pDatasetType.CUI=CUIDatasetType AND r.CUI=pFig2modality.CUI AND cFig2modality.SAB=context
        RETURN DISTINCT tFig2modality.name AS fig2_modality
}
// Fig2 category
CALL
{
        WITH CUIDatasetType,context
        OPTIONAL MATCH (pDatasetType:Concept)-[:has_fig2_category]->(pFig2category:Concept)-[:CODE]->(cFig2category:Code)-[r:PT]->(tFig2category:Term)
        WHERE pDatasetType.CUI=CUIDatasetType AND r.CUI=pFig2category.CUI AND cFig2category.SAB=context
        RETURN DISTINCT tFig2category.name AS fig2_category
}

// Get assaytypes associated with dataset type.
CALL {
    WITH CUIDatasetType, context
    OPTIONAL MATCH (pDatasetType:Concept {CUI:CUIDatasetType})<-[:has_dataset_type]-
                   (pAssayClass:Concept)-[:CODE]->
                   (cAssayClass:Code {SAB:context})-[rAssayClass:PT {CUI:pAssayClass.CUI}]->
                   (tAssayClass:Term),
                   (pAssayClass:Concept)-[:has_assaytype]->
                   (pAssayType:Concept)-[:CODE]->
                   (cAssayType:Code {SAB:context})-[rAssayType:PT {CUI:pAssayType.CUI}]->
                   (tAssayType:Term)
    WITH cAssayType.CODE AS CodeAssayType, tAssayType.name AS NameAssayType
    WHERE CodeAssayType IS NOT NULL
    RETURN collect(DISTINCT  NameAssayType) AS assaytypes
}

// Get whether an Epic datatype.
CALL {
    WITH CUIDatasetType, context
    OPTIONAL MATCH (pDatasetType:Concept {CUI:CUIDatasetType})-[:isa]->
                   (pEpic:Concept)-[:CODE]->
                   (cEpic:Code {SAB:context})
    WHERE cEpic.CODE = 'C004034'
    RETURN CASE WHEN count(pEpic) > 0 THEN true ELSE false END AS is_externally_processed
}

WITH CodeDatasetType, NameDatasetType, assaytypes, is_externally_processed, context,
     CASE
       WHEN epictype_filter = 'true' THEN true
       WHEN epictype_filter = 'false' THEN false
       ELSE null
     END AS epictype_filter_bool,
pdr_category,fig2_aggregated_assaytype,fig2_modality,fig2_category
  WHERE (epictype_filter_bool IS NULL OR is_externally_processed = epictype_filter_bool)

// Stream response.
WITH {
        dataset_type:NameDatasetType,
        assaytypes:assaytypes,
        is_externally_processed:is_externally_processed,
        PDR_category:pdr_category,
        fig2: {
                       aggregated_assaytype: fig2_aggregated_assaytype,
                       modality:             fig2_modality,
                       category:             fig2_category
                     }
        } AS dataset_type
WITH DISTINCT dataset_type AS dataset_types
WHERE dataset_types IS NOT NULL
RETURN collect(DISTINCT dataset_types) AS dataset_types
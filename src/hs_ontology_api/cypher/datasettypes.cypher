// Called by the dataset-types endpoint.

// Return information on dataset types.

// Obtain identifiers for rule-based datasets (assay classes) for the application context.
// The assayclass_filter allows filtering by either the UBKG code or term (rule_description)
// for the assay class.
WITH '$context' AS context
CALL
{
        WITH context
        MATCH (t:Term)<-[rp:PT]-(c:Code)<-[:CODE]-(p:Concept)<-[:isa]-(pDatasetType:Concept)-[:CODE]->(cDatasetType:Code)-[r:PT]->(tDatasetType:Term)
        WHERE c.CodeID = context+':C003041'
        AND rp.CUI=p.CUI
        AND r.CUI=pDatasetType.CUI
        AND cDatasetType.SAB=context
        $datasettype_filter
        RETURN DISTINCT pDatasetType.CUI AS CUIDatasetType,tDatasetType.name AS dataset_type
        ORDER BY dataset_type
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
// assaytypes
CALL
{
        WITH CUIDatasetType,context
        OPTIONAL MATCH (pDatasetType:Concept)<-[:has_dataset_type]-(pAssayClass:Concept)-[:CODE]->(cAssayClass:Code)-[r:PT]->(tAssayClass:Term),
        (pAssayClass:Concept)-[:has_assaytype]->(pAssayType:Concept)-[:CODE]-(cAssayType:Code)-[r2:PT]->(tAssayType:Term)
        WHERE pDatasetType.CUI = CUIDatasetType
        AND r.CUI = pAssayClass.CUI
        AND r2.CUI = pAssayType.CUI
        AND cAssayClass.SAB=context
        AND cAssayType.SAB=context
        RETURN COLLECT(DISTINCT tAssayType.name) AS assaytypes
}
// Whether an Epic datatype
CALL
{
   WITH CUIDatasetType,context
   OPTIONAL MATCH (pDatasetType:Concept)-[:isa]->(pEpic:Concept)-[:CODE]->(cEpic:Code)
   WHERE pDatasetType.CUI = CUIDatasetType
   AND cEpic.CODE = 'C004034'
   AND cEpic.SAB = context
   RETURN DISTINCT CASE WHEN pEpic IS NULL THEN false ELSE true END AS is_externally_processed
}
WITH  dataset_type,pdr_category,fig2_aggregated_assaytype,fig2_modality,fig2_category,assaytypes,is_externally_processed
$epictype_filter
RETURN
{
        dataset_type:dataset_type,
        PDR_category:pdr_category,
        fig2:
        {
            aggregated_assaytype:fig2_aggregated_assaytype,
            modality:fig2_modality,
            category:fig2_category
        },
        assaytypes:assaytypes,
        is_externally_processed:is_externally_processed
} AS dataset_types

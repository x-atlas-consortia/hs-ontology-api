// Called by the assayclassifier endpoint.

// Return information on rule-based datasets--i.e., the datasets specified in the Rule Engine's testing rule chain.

// Obtain identifiers for rule-based datasets (assay classes) for the application context.
// The assayclass_filter allows filtering by either the UBKG code or term (rule_description)
// for the assay class.
// OCT 2024 - filter response content based on
// 1. whether to provide dataset type hierarchical information
// 2. whether to provide measurement assay codes

WITH '$context' AS context, '$provide_hierarchy_info' AS provide_hierarchy_info
CALL
{
        WITH context
        MATCH (p:Concept)<-[:isa]-(pRBD:Concept)-[:CODE]->(cRBD:Code)-[r:PT]->(tRBD:Term)
        WHERE p.CUI = context+':C000004 CUI'
        AND r.CUI=pRBD.CUI
        $assayclass_filter
        RETURN pRBD.CUI AS CUIRBD,cRBD.CODE AS CodeRBD,tRBD.name AS NameRBD
        ORDER BY pRBD.CUI
}
// assaytype
CALL
{
        WITH CUIRBD, context
        MATCH (pRBD:Concept)-[:has_assaytype]->(passaytype:Concept)-[:CODE]->(cassaytype:Code)-[r:PT]->(tassaytype:Term)
        WHERE pRBD.CUI=CUIRBD
        $assaytype_filter
        AND r.CUI=passaytype.CUI and cassaytype.SAB=context
        RETURN DISTINCT REPLACE(tassaytype.name,'_assaytype','') AS assaytype
}
// dir-schema
CALL
{
        WITH CUIRBD,context
        OPTIONAL MATCH (pRBD:Concept)-[:has_dir_schema]->(pdir_schema:Concept)-[:CODE]-(cdir_schema:Code)-[r:PT]->(tdir_schema:Term)
        WHERE pRBD.CUI=CUIRBD AND r.CUI=pdir_schema.CUI AND cdir_schema.SAB=context
        RETURN DISTINCT tdir_schema.name AS dir_schema
}
// tbl-schema
CALL
{
        WITH CUIRBD,context
        OPTIONAL MATCH (pRBD:Concept)-[:has_tbl_schema]->(ptbl_schema:Concept)-[:CODE]->(ctbl_schema:Code)-[r:PT]->(ttbl_schema:Term)
        WHERE pRBD.CUI=CUIRBD AND r.CUI=ptbl_schema.CUI AND ctbl_schema.SAB=context
        RETURN DISTINCT ttbl_schema.name AS tbl_schema
}
// vitessce_hints
// Strip the optional suffix '_vitessce_hint' from terms such as 'rna_vitessce_hint'.
CALL
{
        WITH CUIRBD,context
        OPTIONAL MATCH (pRBD:Concept)-[:has_vitessce_hint]->(pvitessce_hint:Concept)-[:CODE]->(cvitessce_hint:Code)-[r:PT]->(tvitessce_hint:Term)
        WHERE pRBD.CUI=CUIRBD AND r.CUI=pvitessce_hint.CUI AND cvitessce_hint.SAB=context
        RETURN COLLECT(DISTINCT REPLACE(tvitessce_hint.name,'_vitessce_hint','')) AS vitessce_hints
}
// process state. The process_state_filter allows for filtering to just primary or derived assay classes.
CALL
{
        WITH CUIRBD,context
        MATCH (pRBD:Concept)-[:has_process_state]->(pdsProcess:Concept)-[:isa]->(pProcessParent:Concept),
        (pdsProcess:Concept)-[:CODE]->(cdsProcess:Code)-[r:PT]->(tdsProcess:Term)
        WHERE pRBD.CUI=CUIRBD
        AND pProcessParent.CUI = context+':C004002 CUI'
        AND r.CUI=pdsProcess.CUI
        AND cdsProcess.SAB=context
        $process_state_filter
        RETURN tdsProcess.name as process_state
}
// dataset_type

// The dataset_type concepts in HUBMAP are cross-referenced to HRAVS concepts; however, the terms for the HRAVS concepts
// are enclosed in a list, so use the HUBMAP terms.
CALL
{
    WITH CUIRBD,context
    OPTIONAL MATCH (pRBD:Concept)-[:has_dataset_type]->(pdataset_type:Concept)-[:CODE]->(cdataset_type:Code)-[r:PT]->(tdataset_type:Term)
    WHERE pRBD.CUI=CUIRBD AND r.CUI=pdataset_type.CUI AND cdataset_type.SAB=context
    RETURN DISTINCT tdataset_type.name AS dataset_type, pdataset_type.CUI AS CUIDatasetType
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
// dataset_type summary
// Oct 2024 - content driven by provide_hierarchy_info parameter.
CALL
{
    WITH dataset_type, pdr_category, fig2_aggregated_assaytype, fig2_modality, fig2_category, provide_hierarchy_info
    RETURN
    CASE
        WHEN provide_hierarchy_info='True'
        THEN
                {
                        dataset_type:dataset_type,
                        PDR_category:pdr_category,
                        fig2:
                        {
                                aggregated_assaytype:fig2_aggregated_assaytype,
                                modality:fig2_modality,
                                category:fig2_category
                        }
                }
        ELSE
            dataset_type
        END AS dataset_type_summary
}
// description
CALL
{
        WITH CUIRBD,context
        OPTIONAL MATCH (pRBD:Concept)-[:has_description]->(pdescription:Concept)-[:CODE]->(cdescription:Code)-[r:PT]->(tdescription:Term)
        WHERE pRBD.CUI=CUIRBD AND r.CUI=pdescription.CUI AND cdescription.SAB=context
        RETURN DISTINCT REPLACE(tdescription.name,'_description','') AS description
}
// pipeline-shorthand
CALL
{
        WITH CUIRBD,context
        OPTIONAL MATCH (pRBD:Concept)-[:has_pipeline_shorthand]->(pshorthand:Concept)-[:CODE]->(cshorthand:Code)-[r:PT]->(tshorthand:Term)
        WHERE pRBD.CUI=CUIRBD and r.CUI=pshorthand.CUI AND cshorthand.SAB=context
        RETURN DISTINCT tshorthand.name AS pipeline_shorthand
}
// is multi-assay
CALL
{
        WITH CUIRBD, context
        OPTIONAL MATCH (pRBD:Concept)-[:isa]->(pMulti:Concept)
        WHERE pRBD.CUI=CUIRBD
        AND pMulti.CUI = context+':C004033 CUI'
        RETURN DISTINCT CASE WHEN pMulti.CUI IS NOT NULL THEN True ELSE False END AS is_multiassay
}
// must_contain
CALL
{
        WITH CUIRBD,context
        OPTIONAL MATCH (pRBD:Concept)-[:must_contain]->(pDT:Concept)-[:CODE]-(cDT:Code)-[r:PT]->(tDT:Term)
        WHERE pRBD.CUI=CUIRBD AND r.CUI=pDT.CUI AND cDT.SAB=context
        RETURN COLLECT(DISTINCT tDT.name) AS must_contain
}

// whether the assay classification contains full_genetic_sequences
CALL
{
        WITH CUIRBD,context
        OPTIONAL MATCH (pRBD:Concept)-[:contains]->(ppii:Concept)
        WHERE pRBD.CUI=CUIRBD
        AND ppii.CUI = context+':C004009 CUI'
        RETURN DISTINCT CASE WHEN NOT ppii.CUI IS null THEN true ELSE false END AS contains_full_genetic_sequences
}

// active status
CALL
{
        WITH CUIRBD,context
        OPTIONAL MATCH (pRBD:Concept)-[:has_active_status]->(pStatus:Concept)-[:CODE]->(cStatus:Code)-[r:PT]->(tStatus:Term)
        WHERE pRBD.CUI=CUIRBD AND r.CUI=pStatus.CUI and cStatus.SAB=context
        RETURN DISTINCT tStatus.name AS active_status
}
// Response
CALL
{
WITH
context, CodeRBD, NameRBD, assaytype, dir_schema, tbl_schema,
vitessce_hints,process_state,pipeline_shorthand,
description,dataset_type_summary,
is_multiassay,must_contain,active_status, contains_full_genetic_sequences
RETURN
{
        rule_description:
        {       code:CodeRBD,application_context:context, name:NameRBD
        },
        value:
        {
                assaytype:assaytype, dir_schema:dir_schema, tbl_schema:tbl_schema, vitessce_hints:vitessce_hints,
                process_state:process_state,
                pipeline_shorthand:pipeline_shorthand, description:description,
                is_multiassay:is_multiassay, must_contain:must_contain,
                active_status:active_status,
                dataset_type:dataset_type_summary,
                contains_full_genetic_sequences:contains_full_genetic_sequences
        }
}
AS rule_based_dataset
}
WITH rule_based_dataset
RETURN rule_based_dataset AS rule_based_datasets

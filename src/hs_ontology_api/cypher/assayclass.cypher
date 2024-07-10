// Called by the assayclassifier endpoint.

// Return information on rule-based datasets--i.e., the datasets specified in the Rule Engine's testing rule chain.

// Obtain identifiers for rule-based datasets (assay classes) for the application context.
WITH '$context' AS context
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
	WITH CUIRBD
	MATCH (pRBD:Concept)-[:has_assaytype]->(passaytype:Concept)-[:PREF_TERM]->(tassaytype:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN REPLACE(tassaytype.name,'_assaytype','') AS assaytype
}
// dir-schema
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_dir_schema]->(pdir_schema:Concept)-[:PREF_TERM]->(tdir_schema:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN tdir_schema.name AS dir_schema
}
// tbl-schema
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_tbl_schema]->(ptbl_schema:Concept)-[:PREF_TERM]->(ttbl_schema:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN ttbl_schema.name AS tbl_schema
}
// vitessce_hints
// Strip the optional suffix '_vitessce_hint' from terms such as 'rna_vitessce_hint'.
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_vitessce_hint]->(pvitessce_hint:Concept)-[:PREF_TERM]->(tvitessce_hint:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN COLLECT(REPLACE(tvitessce_hint.name,'_vitessce_hint','')) AS vitessce_hints
}
// is_primary
CALL
{
	WITH CUIRBD,context
	OPTIONAL MATCH (pRBD:Concept)-[:has_process_state]->(pdsProcess:Concept)-[:isa]->(pProcessParent:Concept)
	WHERE pRBD.CUI=CUIRBD
	AND pProcessParent.CUI = context+':C004002 CUI'
	RETURN CASE WHEN pdsProcess.CUI=context+':C004003 CUI' THEN true else false END AS is_primary
}
// dataset_type
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_dataset_type]->(pdataset_type:Concept)-[:PREF_TERM]->(tdataset_type:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN tdataset_type.name AS dataset_type, pdataset_type.CUI AS CUIDatasetType
}
// Pipeline Decision Rules category
CALL
{
	WITH CUIDatasetType
	OPTIONAL MATCH (pDatasetType:Concept)-[:has_pdr_category]->(pPDRCategory:Concept)-[:PREF_TERM]->(tPDRCategory:Term)
	WHERE pDatasetType.CUI=CUIDatasetType
	RETURN tPDRCategory.name AS pdr_category
}
// Fig 2 aggregated assay type
CALL
{
	WITH CUIDatasetType
	OPTIONAL MATCH (pDatasetType:Concept)-[:has_fig2_agg_assay_type]->(pFig2agg:Concept)-[:PREF_TERM]->(tFig2agg:Term)
	WHERE pDatasetType.CUI=CUIDatasetType
	RETURN tFig2agg.name AS fig2_aggregated_assaytype
}
// Fig2 modality
CALL
{
	WITH CUIDatasetType
	OPTIONAL MATCH (pDatasetType:Concept)-[:has_fig2_modality]->(pFig2modality:Concept)-[:PREF_TERM]->(tFig2modality:Term)
	WHERE pDatasetType.CUI=CUIDatasetType
	RETURN tFig2modality.name AS fig2_modality
}
// Fig2 category
CALL
{
	WITH CUIDatasetType
	OPTIONAL MATCH (pDatasetType:Concept)-[:has_fig2_category]->(pFig2category:Concept)-[:PREF_TERM]->(tFig2category:Term)
	WHERE pDatasetType.CUI=CUIDatasetType
	RETURN tFig2category.name AS fig2_category
}
// description
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_description]->(pdescription:Concept)-[:PREF_TERM]->(tdescription:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN REPLACE(tdescription.name,'_description','') AS description
}
// pipeline-shorthand
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_pipeline_shorthand]->(pshorthand:Concept)-[:PREF_TERM]->(tshorthand:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN tshorthand.name AS pipeline_shorthand
}
// is multi-assay
CALL
{
	WITH CUIRBD, context
	OPTIONAL MATCH (pRBD:Concept)-[:isa]->(pMulti:Concept)
	WHERE pRBD.CUI=CUIRBD
	AND pMulti.CUI = context+':C004033 CUI'
	RETURN CASE WHEN pMulti.CUI IS NOT NULL THEN True ELSE False END AS is_multiassay
}
// must_contain
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:must_contain]->(pDT:Concept)-[:PREF_TERM]->(tDT:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN COLLECT(tDT.name) AS must_contain
}
// measurement assay CUI
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_measurement_assay]->(pMeas:Concept)
	WHERE pRBD.CUI=CUIRBD
	RETURN pMeas.CUI as CUIMeas
}
// Optional measurement codes
CALL
{
	WITH CUIMeas
	MATCH (pMeas:Concept)-[:CODE]->(cMeas:Code)-[:PT]->(tMeas:Term)
	WHERE pMeas.CUI = CUIMeas
	RETURN COLLECT(DISTINCT {code:cMeas.CodeID,term:tMeas.name}) AS MeasCodes
}
// whether the measurement assay contains full_genetic_sequencesi
CALL
{
	WITH CUIMeas,context
	OPTIONAL MATCH (pRBD:Concept)-[:contains]->(ppii:Concept)
	WHERE pRBD.CUI=CUIMeas
	AND ppii.CUI = context+':C004009 CUI'
	RETURN CASE WHEN NOT ppii.CUI IS null THEN true ELSE false END AS contains_full_genetic_sequences
}
// provider
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_provider]->(pProvider:Concept)-[:PREF_TERM]->(tProvider:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN tProvider.name AS provider
}
// active status
CALL
{
	WITH CUIRBD
	OPTIONAL MATCH (pRBD:Concept)-[:has_active_status]->(pStatus:Concept)-[:PREF_TERM]->(tStatus:Term)
	WHERE pRBD.CUI=CUIRBD
	RETURN tStatus.name AS active_status
}
CALL
{
WITH CodeRBD, NameRBD, assaytype, dir_schema, tbl_schema, vitessce_hints,is_primary,pipeline_shorthand,description,dataset_type,pdr_category,fig2_aggregated_assaytype,fig2_modality,fig2_category,is_multiassay,must_contain,MeasCodes,contains_full_genetic_sequences,provider,active_status
RETURN
{
	rule_description:
	{	code:CodeRBD,name:NameRBD
	},
	value:
	{
		assaytype:assaytype, dir_schema:dir_schema, tbl_schema:tbl_schema, vitessce_hints:vitessce_hints, primary:is_primary,
		pipeline_shorthand:pipeline_shorthand, description:description,
		is_multiassay:is_multiassay, must_contain:must_contain,
		provider:provider,
		active_status:active_status,
		dataset_type:
		{
			dataset_type:dataset_type, PDR_category:pdr_category,
			fig2:
			{
				aggregated_assaytype:fig2_aggregated_assaytype, modality:fig2_modality, category:fig2_category
			}
		},
		measurement_assay:{
			codes:MeasCodes,
			contains_full_genetic_sequences:contains_full_genetic_sequences
		}
	}
} AS rule_based_dataset
}
WITH rule_based_dataset
RETURN rule_based_dataset AS rule_based_datasets
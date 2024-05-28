// Called by the following endpoints:
// datasets
// assayname
// assaytype

// Filter by the application context.
WITH $context AS context

// Obtain the set of CUIs for the values of data_type for datasets. data_type is the key for workflow DAGs. The Rule Engine refers to data_type as "assaytype".
CALL
{
	WITH context
	MATCH (cParent:Code)<-[:CODE]-(pParent:Concept)<-[:isa]-(pChild:Concept)-[rConceptTerm:PREF_TERM]->(tChild:Term)
	WHERE cParent.CodeID = apoc.text.join([context,':C004001'],'')
	RETURN pChild.CUI AS data_typeCUI, tChild.name AS data_type
	ORDER BY tChild.name
}
// For each data_type, obtain the corresponding Dataset concept--i.e., the "HubMAP Dataset" or "SenNet Dataset".
CALL
{
	WITH data_typeCUI,context
	OPTIONAL MATCH (pDataType:Concept)<-[r:has_data_type]-(pDataset:Concept)
	WHERE r.SAB = context
	AND pDataType.CUI = data_typeCUI
	RETURN pDataset.CUI AS DatasetCUI
}
// For each Dataset, obtain the description.
CALL
{
	WITH DatasetCUI, context
	OPTIONAL MATCH (pDatasetThing:Concept)-[rProperty:has_display_name]->(pProperty:Concept)-[rConceptTerm:PREF_TERM]->(tProperty:Term)
	WHERE pDatasetThing.CUI = DatasetCUI
	AND rProperty.SAB = context
	RETURN CASE tProperty.name WHEN NULL THEN '' ELSE tProperty.name END  AS description
}
// For each data_type, obtain the set of alt-names.
CALL
{
	WITH data_typeCUI,context
	OPTIONAL MATCH (pDatasetThing:Concept)-[:CODE]->(cDatasetThing:Code)-[rCodeTerm:SY]->(tSyn:Term)
	WHERE cDatasetThing.SAB = context
	AND rCodeTerm.CUI = pDatasetThing.CUI
	AND pDatasetThing.CUI = data_typeCUI
	RETURN COLLECT(tSyn.name)  AS alt_names
}
// For each dataset, obtain whether the dataset is primary.
CALL
{
	WITH DatasetCUI,context
	OPTIONAL MATCH (pDatasetThing:Concept)-[rProperty:isa]->(pProperty:Concept)-[:CODE]->(cProperty:Code)-[rCodeTerm:PT]->(tProperty:Term)
	WHERE pDatasetThing.CUI = DatasetCUI
	AND rProperty.SAB = context
	AND cProperty.SAB = context
	AND rCodeTerm.CUI = pProperty.CUI
	AND cProperty.CODE IN ['C004003','C004004']
	RETURN CASE cProperty.CODE WHEN 'C004003' THEN true WHEN 'C004004' THEN false ELSE '' END  AS primary
}
// For each Dataset, obtain the dataset provider--either the IEC or an external provider.
CALL
{
	WITH DatasetCUI,context
	OPTIONAL MATCH (pDatasetThing:Concept)-[rProperty:provided_by]->(pProperty:Concept)-[rConceptTerm:PREF_TERM]->(tProperty:Term)
	WHERE pDatasetThing.CUI = DatasetCUI
	AND rProperty.SAB = context
	RETURN CASE tProperty.name WHEN NULL THEN '' ELSE tProperty.name END  AS dataset_provider
}
// For each Dataset, obtain whether the Dataset is vis-only.
CALL
{
	WITH DatasetCUI,context
	OPTIONAL MATCH (pDatasetThing:Concept)-[rProperty:isa]->(pProperty:Concept)-[:CODE]->(cProperty:Code)-[rCodeTerm:PT]->(tProperty:Term)
	WHERE pDatasetThing.CUI = DatasetCUI
	AND rProperty.SAB = context
	AND cProperty.SAB = context
	AND rCodeTerm.CUI = pProperty.CUI
	AND cProperty.CODE IN ['C004008']
	RETURN cProperty.CodeID IS NOT NULL AS vis_only
}
// For each Dataset, obtain whether the Dataset contains PII.
CALL
{
	WITH DatasetCUI,context
	OPTIONAL MATCH (pDatasetThing:Concept)-[rProperty:contains]->(pProperty:Concept)-[:CODE]->(cProperty:Code)-[rCodeTerm:PT]->(tProperty:Term)
	WHERE pDatasetThing.CUI = DatasetCUI
	AND rProperty.SAB = context
	AND cProperty.SAB = context
	AND rCodeTerm.CUI = pProperty.CUI
	AND cProperty.CODE IN ['C004009']
	RETURN cProperty.CodeID IS NOT NULL  AS contains_pii
}
// For each data_type, obtain the list of vitessce hints. Some vitessce_hint concepts contain the suffix "_vitessce_hint", which should be removed.
CALL
{
	WITH data_typeCUI,context
	OPTIONAL MATCH (pDatasetThing:Concept)-[rProperty:has_vitessce_hint]->(pProperty:Concept)-[rConceptTerm:PREF_TERM]->(tProperty:Term)
	WHERE pDatasetThing.CUI = data_typeCUI
	AND rProperty.SAB = context
	RETURN COLLECT(REPLACE(tProperty.name,'_vitessce_hint','')) AS vitessce_hints
}
// For each Dataset, return the Dataset Type.
CALL
{
	WITH DatasetCUI,context
	OPTIONAL MATCH (pDataset:Concept)-[:isa]->(pDatasetType:Concept)-[:isa]-(pParent:Concept),
	(pDatasetType:Concept)-[:CODE]->(cDatasetType:Code)-[:PT]->(tDatasetType:Term)
	WHERE pDataset.CUI = DatasetCUI
	AND pParent.CUI = 'HRAVS:1000361 CUI'
	AND cDatasetType.SAB = context
	RETURN DISTINCT tDatasetType.name AS dataset_type, pDatasetType.CUI AS DatasetTypeCUI
}
// For each Dataset, determine whether active or inactive.
CALL
{
	WITH DatasetCUI,context
	OPTIONAL MATCH (pDataset:Concept)-[:isa]->(p2:Concept)-[:CODE]->(c2:Code)-[:PT]->(t2:Term)
	WHERE pDataset.CUI = DatasetCUI
	AND c2.SAB=context
	AND CASE WHEN context='HUBMAP' THEN c2.CODE IN ['C004030','C004031'] ELSE c2.CODE IN ['C004022','C0040023'] END
	RETURN DISTINCT t2.name AS dataset_active
}
// For each Dataset type, determine whether active or inactive.
CALL
{
	WITH DatasetTypeCUI,context
	OPTIONAL MATCH (pDataset:Concept)-[:isa]->(p2:Concept)-[:CODE]->(c2:Code)-[:PT]->(t2:Term)
	WHERE pDataset.CUI = DatasetTypeCUI
	AND c2.SAB=context
	AND CASE WHEN context='HUBMAP' THEN c2.CODE IN ['C004030','C004031'] ELSE c2.CODE IN ['C004022','C0040023'] END
	RETURN DISTINCT t2.name AS dataset_type_active
}
// For each assay classification, return the measurement assay.
CALL
{
  WITH DatasetCUI, context
  MATCH (pDataset:Concept)<-[:has_dataset]-(pAssay_classification:Concept)-[:has_measurement_assay]->(pMeas:Concept)-[:CODE]->(cMeas:Code)-[rMeas:PT]->(tMeas:Term)
  WHERE pDataset.CUI=DatasetCUI
  AND CASE WHEN context = 'HUBMAP' THEN NOT cMeas.SAB = 'SENNET'  WHEN context = 'SENNET' THEN NOT cMeas.SAB = 'HUBMAP' END
  RETURN COLLECT(DISTINCT{code:cMeas.CodeID,term:tMeas.name}) AS measurement_assay
}
// Apply filters.
WITH data_type,description,alt_names,primary,dataset_provider,vis_only,contains_pii,vitessce_hints,dataset_type,dataset_active,dataset_type_active,measurement_assay
// The default filters are that both the assay type and dataset type are active.
// WHERE dataset_active='Active'
// AND dataset_type_active='Active'
// Optional filters
// AND data_type='10x-multiome'
// AND description='10X Multiome'
// AND 'DESI-IMS' IN alt_names
// AND primary = false
// AND contains_pii = true
// AND vis_only = true
// AND 'is_image' IN vitessce_hints
// AND toUpper(dataset_provider) =~ '.*IEC.*'
$optional_filters

// Note the use of back-ticking for the vis-only key.
WITH COLLECT({data_type:data_type,description:description,alt_names:alt_names,primary:primary,
dataset_provider:dataset_provider,`vis-only`:vis_only,
contains_pii:contains_pii,vitessce_hints:vitessce_hints,
dataset_type:dataset_type,
dataset_active:dataset_active,
dataset_type_active:dataset_type_active,
measurement_assay:measurement_assay})
AS assay_classifications
RETURN assay_classifications


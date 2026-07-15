// Called by the dataset-types/hierarchy endpoint.

// Return information on dataset types.
// Only return for the following cases:
// 1. All code filters are ''.
// 2. Each code filter corresponds to a valid code.

// The dataset-types endpoint "filtering path" is a
// directed combination of codes that indicate increasing levels of specificity:
// - all dataset types
// - specific dataset type
// - specific dataset type/specific modality
// - specific dataset type/specificy modality/specific analyte


// The dataset type/modality/analyte hierarchy is defined
// only in the Sennet context.
WITH 'SENNET' AS context,

// Filters:
// Application context--always SENNET
//WITH $context AS context,
// Optional filter: whether an EPIC (externally processed)
$epictype_filter AS epictype_filter,
// Optional filter: Dataset type code
$dataset_type_code AS dataset_type_code,
// Optional filter: Modality code
$modality_code AS modality_code,
// Optional filter: Analyte code
$analyte_code AS analyte_code

// -------
// Get dataset types, optionally filtered on dataset type code.
// - Dataset type nodes are children of the "dataset type" parent (C003041).
// - Term nodes are filtered to those that share the CUI of the associated concept.

WITH
    context,
    dataset_type_code,
    modality_code,
    analyte_code
MATCH
    (tDatasetTypeParent:Term)<-[rDatasetTypeParent:PT {CUI:pDatasetTypeParent.CUI}]-
    (cDatasetTypeParent:Code{SAB:context,CODE:'C003041'})<-[:CODE]-
    (pDatasetTypeParent:Concept)<-[:isa]-
    (pDatasetType:Concept)-[:CODE]->
    (cDatasetType:Code {SAB:context})-[rDatasetType:PT {CUI:pDatasetType.CUI}]->
    (tDatasetType:Term)
WHERE
    (dataset_type_code = '' OR cDatasetType.CODE = dataset_type_code)

WITH
    context,
    modality_code,
    analyte_code,
    pDatasetType.CUI AS CUIDatasetType,
    cDatasetType.CODE AS CodeDatasetType,
    tDatasetType.name AS NameDatasetType

// ---------
// Get associated modalities.
// Modality concept nodes are children of SENNET:C046000 CUI.

WITH
    context,
    modality_code,
    analyte_code,
    CUIDatasetType,
    CodeDatasetType,
    NameDatasetType
 MATCH
    (pDataSetType:Concept {CUI:CUIDatasetType})-[:has_modality]->
    (pModality:Concept)-[:isa]->
    (pModalityParent:Concept)-[:CODE]->
    (cModalityParent:Code{SAB:context,CODE:'C046000'}),
    (pModality:Concept)-[:CODE]->
    (cModality:Code {SAB:context})-[rModality:PT {CUI:pModality.CUI}]->
    (tModality:Term)
WHERE (modality_code = '' OR cModality.CODE = modality_code)

//----------
// Get analytes. The set of analytes is the intersection of the sets of analytes linked to the modalities
// and the sets of analytes linked to the dataset types.
// Analyte nodes are children of the "analyte" parent node (SENNET:C002031).

WITH
    context,
    modality_code,
    analyte_code,
    CUIDatasetType,
    CodeDatasetType,
    NameDatasetType,
    pModality.CUI AS CUIModality,
    cModality.CODE AS CodeModality,
    tModality.name AS NameModality

// Get analytes associated with the dataset types.
WITH
    context,
    modality_code,
    analyte_code,
    CUIDatasetType,
    CodeDatasetType,
    NameDatasetType,
    CUIModality,
    CodeModality,
    NameModality
 MATCH
    (pDatasetType:Concept{CUI:CUIDatasetType})-[:has_analyte]->
    (pAnalyteDatasetType:Concept)-[:isa]->
    (pAnalyteParent:Concept)-[:CODE]->
    (cAnalyteParent:Code {SAB:context,CODE:'C002031'})


// Get analytes associated with modalities.
WITH
    context,
    modality_code,
    analyte_code,
    CUIDatasetType,
    CodeDatasetType,
    NameDatasetType,
    COLLECT(DISTINCT pAnalyteDatasetType.CUI) AS CUIAnalyteDatasetTypes,
    CUIModality,
    CodeModality,
    NameModality
MATCH
    (pModality:Concept{CUI:CUIModality})-[:has_analyte]->
    (pAnalyteModality:Concept)-[:isa]->
    (pAnalyteParent:Concept)-[:CODE]->
    (cAnalyteParent:Code {SAB:context,CODE:'C002031'})

// Find the analytes in the intersection of dataset type and modality.
WITH
    context,
    analyte_code,
    CUIDatasetType,
    CodeDatasetType,
    NameDatasetType,
    CUIAnalyteDatasetTypes,
    CUIModality,
    CodeModality,
    NameModality,
    COLLECT(DISTINCT pAnalyteModality.CUI) AS CUIAnalyteModalities


WITH
    context,
    analyte_code,
    CUIDatasetType,
    CodeDatasetType,
    NameDatasetType,
    CUIAnalyteDatasetTypes,
    CUIModality,
    CodeModality,
    NameModality,
    CUIAnalyteModalities,
    apoc.coll.intersection(CUIAnalyteDatasetTypes, CUIAnalyteModalities) AS CUIAnalytes

// Get codes and terms for analytes, with optional filter for analyte code.
WITH
    context,
    analyte_code,
    CodeDatasetType,
    NameDatasetType,
    CodeModality,
    NameModality,
    CUIAnalytes
UNWIND CUIAnalytes AS CUIAnalyte

WITH
    context,
    analyte_code,
    CodeDatasetType,
    NameDatasetType,
    CodeModality,
    NameModality,
    CUIAnalyte
MATCH
    (pAnalyte:Concept{CUI:CUIAnalyte})-[:CODE]->
    (cAnalyte:Code{SAB:context})-[:PT{CUI:pAnalyte.CUI}]->
    (tAnalyte:Term)
WHERE (analyte_code = '' OR cAnalyte.CODE = analyte_code)

// -------
// Build output.

// Analyte array.
WITH
    CodeDatasetType,
    NameDatasetType,
    CodeModality,
    NameModality,
    COLLECT(DISTINCT {code:cAnalyte.CODE, name:tAnalyte.name}) AS analytes
WHERE size(analytes) > 0

// Modalities array
WITH
    CodeDatasetType,
    NameDatasetType,
    COLLECT(DISTINCT {code:CodeModality, name:NameModality,analytes:analytes}) AS modalities
WHERE size(modalities) >0

// Final output
WITH
    COLLECT(DISTINCT {code:CodeDatasetType, name:NameDatasetType, modalities:modalities}) AS dataset_type
WHERE size(dataset_type) >0

RETURN {dataset_type:dataset_type} AS dataset_type


// PARTICIPANTS FOR PATHWAY
// Returns the participants in a specified Reactome pathway, optionally filtered for SAB.

// Required input filters: an identifier for a Reactome pathway:
// 1. Reactome Stable ID
// 2. Portion of the pathway name, to use with STARTS WITH.

// Optional output filter: a list of "domain SABs", corresponding to participant types to include.
// 1. HGNC - genes
// 2. ENSEMBL - genes (the actual participant reference from Reactome)
// 2. UNIPROTKB - proteins
// 3. CHEBI - molecules
// The default is 'HGNC'.

// Output: list of participants. Each participant will have:
// 1. Code
// 2. symbol (for genes)
// 3. description
///////////////////////////////

// Filters

WITH ['HGNC'] AS defaultsabs,
[$sabs] AS sabs,
//['HGNC','UNIPROTKB'] as sabs,

$pathwayid AS pathwayid,
//'R-HSA-8953897' AS pathwayid, // pathway
//'R-HSA-6803403' AS pathwayid, // reaction
//'Cell' AS pathwayid,

// ENSEMBl feature types--e.g., transcripts or genes
['gene'] AS default_featuretypes,
[$featuretypes] AS featuretypes

//Get CUI for the pathway(s).
CALL
{
	WITH pathwayid
	MATCH (tPathwayType:Term)<-[rPathwayType:PT]-(cPathwayType:Code{SAB:'REACTOME_VS'})<-[:CODE]-(pPathwayType:Concept)-[:inverse_isa{SAB:'REACTOME'}]->(pPathway:Concept)-[:CODE]->(cPathway:Code {SAB:'REACTOME'})-[rPathway:PT]->(tPathway:Term)
	WHERE rPathway.CUI=pPathway.CUI
	AND rPathwayType.CUI=pPathwayType.CUI
	// May 2025 case insensitive
	AND (cPathway.CODE=pathwayid OR lower(tPathway.name) STARTS WITH lower(pathwayid))
	RETURN pPathway.CUI AS PathwayCUI,cPathway.CODE as PathwayCode, tPathway.name AS PathwayName,tPathwayType.name AS PathwayType
}

// Expand the event hierarchy from pathway down to the reaction (lowest level).
// The maximum depth of the Reactome event hierarchy is 8 hops from a TopLevelPathway.
// Return unique nodes.
CALL
{
	WITH PathwayCUI
	MATCH (p:Concept{CUI:PathwayCUI})
	CALL apoc.path.expandConfig(p, {
    relationshipFilter: "causally_related_to>",
    minLevel: 0,
    maxLevel: 10,
	uniqueness: "NODE_PATH"
})
YIELD path
RETURN path
}

// Obtain participant CUIs.
CALL
{
	WITH path
	UNWIND nodes(path) as pEvent
	MATCH (pEvent)-[:has_participant{SAB:'REACTOME'}]->(pParticipant:Concept)
	RETURN pParticipant.CUI AS ParticipantCUI
}

// Categorize participants by type.
CALL
{
	//Genes from HGNC
	WITH PathwayCUI,ParticipantCUI
	MATCH (pParticipant:Concept{CUI:ParticipantCUI})-[:CODE]->(cParticipant:Code{SAB:'HGNC'})-[rACR:ACR]-(tSymbol:Term),(cParticipant:Code)-[rPT:PT]->(tDescription:Term)
	WHERE rACR.CUI=pParticipant.CUI AND rPT.CUI=pParticipant.CUI
	RETURN
		cParticipant.SAB AS ParticipantSAB,
		tSymbol.name AS ParticipantSymbol,
		{id:cParticipant.CODE,symbol:tSymbol.name,description:tDescription.name,featuretype:'n/a'} as participant

	UNION
	//participants from UNIPROTKB or CHEBI
	WITH PathwayCUI,ParticipantCUI
	MATCH (pParticipant:Concept{CUI:ParticipantCUI})-[:CODE]->(cParticipant:Code)-[r]-(tParticipant:Term)
	WHERE cParticipant.SAB IN ['UNIPROTKB','CHEBI','OMIM','ENTREZ']
	AND type(r) IN ['PT','PT_GENCODE']
	//AND r.CUI=pParticipant.CUI
	RETURN
		cParticipant.SAB AS ParticipantSAB,
		cParticipant.CODE AS ParticipantSymbol,
		{id:cParticipant.CODE,symbol:cParticipant.CODE,description:tParticipant.name,featuretype:'n/a'} AS participant

	UNION
	// participants from ENSEMBL, which can include both transcripts and genes

	WITH PathwayCUI,ParticipantCUI,featuretypes,default_featuretypes
	MATCH (tFeature:Term)<-[:PT]-(cFeature:Code{SAB:'GENCODE_VS'})<-[:CODE]-(pFeature:Concept)<-[rFeature:is_feature_type]-(pParticipant:Concept{CUI:ParticipantCUI})-[:CODE]->(cParticipant:Code)-[r]-(tParticipant:Term)
	WHERE cParticipant.SAB IN ['ENSEMBL']
	AND type(r) IN ['PT','PT_GENCODE']
	AND CASE
		WHEN featuretypes[0]<>'' THEN ANY(f in featuretypes WHERE toLower(tFeature.name)=toLower(f))
		ELSE ANY(f in default_featuretypes WHERE toLower(tFeature.name)=toLower(f))
		END
	AND r.CUI=pParticipant.CUI
	RETURN
		cParticipant.SAB AS ParticipantSAB,
		cParticipant.CODE AS ParticipantSymbol,
		{id:cParticipant.CODE,symbol:cParticipant.CODE,description:tParticipant.name,featuretype:tFeature.name} AS participant

}
WITH sabs,defaultsabs,ParticipantSAB,ParticipantSymbol,PathwayCUI, PathwayCode,PathwayName, PathwayType, participant
WHERE CASE
	WHEN sabs[0]<>'' THEN ANY(sab IN sabs WHERE toUpper(ParticipantSAB)=toUpper(sab))
	ELSE ANY(sab IN defaultsabs WHERE toUpper(ParticipantSAB)=toUpper(sab))
	END

WITH ParticipantSAB,ParticipantSymbol,PathwayCUI, PathwayCode,PathwayName, PathwayType, participant
ORDER BY PathwayType DESC,PathwayName,ParticipantSAB,ParticipantSymbol

// Collect by pathway, then participants.
WITH ParticipantSAB, PathwayCUI, PathwayCode,PathwayName, PathwayType,COLLECT(DISTINCT participant) AS participants, COUNT(DISTINCT participant) AS participantcount

WITH PathwayCode,PathwayName,PathwayType,COLLECT(DISTINCT {SAB:ParticipantSAB,count:participantcount,participants:participants}) AS pathwaysabs
ORDER BY PathwayType DESC, PathwayName
WITH COLLECT({code:PathwayCode,name:PathwayName,type:PathwayType,sabs:pathwaysabs}) AS pathways,
COUNT(DISTINCT PathwayCode) as pathwaycount
RETURN {count:pathwaycount,events:pathways} AS response
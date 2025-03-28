// PATHWAY EVENTS WITH GENES
// Returns information on the Reactome pathway events that have specified genes as participants.

// Optional input filters:
// 1. HGNC identifiers:
//    The following types of identifiers can be used in the list:
//    a. HGNC numeric IDs (e.g., 7178)
//    b. HGNC approved symbols (e.g., MMRN1)
//    c. HGNC previous symbols (e.g., MMRN)
//    d. HGNC aliases (e.g., ECM)
//    e. names (approved name, previous name, alias name).
//       Because exact matches would be required, it is unlikely that names would be useful criteria.
//    If no criteria are specified, return information on all HGNC genes.
// 2. (pathway) Event identifiers:
//    a. Reactome stable ID
//    b. Portion of the name of an event, to use STARTS WITH
// 3. Reactome event type--a set of one or more of the following types:
//    a. TopLevelPathway
//    b. Pathway
//    c. Reaction
//    d. BlackBoxEvent
//    e. Polymerisation
//    f. Depolymerisation
//       The default event type filter is for the set {TopLevelPathway,Pathway}
//

// Returns list of pathway events, sorted by event type and name.
/////////////////////////////////////////

// Input filters
// The calling function will populate the input filters.
// Gene identifiers
WITH [$geneids] AS geneids,
//WITH [''] AS geneids,
//WITH ['EGFR'] AS geneids,

// Reaction identifiers
$pathwayid AS pathwayid,
//'' AS pathwayid,
//'R-HSA-74160' AS pathwayid,

$pathwayname AS pathwayname,
//'' AS pathwayname,
//'A' AS pathwayname

// Reactome event type
[$eventtypes] AS eventtypes
//'' AS eventtypes,
//[''] AS eventtypes


// Get CUIs of concepts for genes that match the criteria.
CALL
{

	WITH geneids

	// Find CUIs for genes that satisfy criteria for HGNC ID or term (symbol, name).
	// The preferred CUI for each HGNC Code can be identified by the CUI property of any relationship between the code
	// and one of its terms--e.g., PT.

	OPTIONAL MATCH (pGene:Concept)-[:CODE]->(cGene:Code)-[r]->(tGene:Term)
	WHERE r.CUI=pGene.CUI
	AND type(r) IN ['PT','ACR','NS','NP','SYN','NA_UBKG']
	AND cGene.SAB='HGNC'
	AND CASE
		WHEN geneids[0]<>'' THEN (ANY(id IN geneids WHERE cGene.CODE=id) or ANY(id in geneids WHERE tGene.name=id))
		ELSE 1=1 END
	RETURN DISTINCT pGene.CUI AS GeneCUI, toInteger(cGene.CODE) AS GeneCode

}
// Get gene information
CALL
{
	WITH GeneCUI
	MATCH (pGene:Concept{CUI:GeneCUI})-[:CODE]->(cGene:Code{SAB:'HGNC'})-[rGene:ACR]->(tGene:Term)
	WHERE rGene.CUI=pGene.CUI
	RETURN DISTINCT tGene.name AS GeneSymbol
}
CALL
{
	WITH GeneCUI
	OPTIONAL MATCH (pGene:Concept{CUI:GeneCUI})-[:CODE]->(cGene:Code{SAB:'HGNC'})-[rGene:PT]->(tGene:Term)
	WHERE rGene.CUI=pGene.CUI
	RETURN DISTINCT tGene.name AS GeneDescription
}

// Find Reactome reactions for which the gene is a participant. Participants associate at the level of "reaction-type event" in the Reactome event hierarchy, including event types of "Reaction" and "BlackBoxEvent".
CALL
{
	WITH GeneCUI
	MATCH (pGene:Concept)<-[r:has_participant {SAB:'REACTOME'}]-(pReaction:Concept)
	WHERE pGene.CUI=GeneCUI
	RETURN pReaction.CUI AS ReactionCUI
}

// From each reaction, expand the event hierarchy from the reaction (lowest level) up to the TopLevelPathway (highest level).
// The maximum depth of the Reactome event hierarchy is 8 hops from a TopLevelPathway.
// Return unique nodes.

CALL
{
	WITH ReactionCUI
	MATCH (p:Concept{CUI:ReactionCUI})
	CALL apoc.path.expandConfig(p, {
    relationshipFilter: "<causally_related_to",
    minLevel: 1,
    maxLevel: 10,
	uniqueness: "NODE_PATH"
})
YIELD path
RETURN path
}

// Filter to those paths that involve REACTOME relationships.
WITH GeneCUI,GeneCode,GeneSymbol,GeneDescription,path,pathwayid,pathwayname,eventtypes
WHERE ALL(r IN relationships(path) WHERE r.SAB='REACTOME')

// For each event in each path, return the Reactome Stable ID and name
WITH path,pathwayid,pathwayname,eventtypes
UNWIND nodes(path) as pEvent

CALL
{
	WITH pathwayid, pathwayname, pEvent, eventtypes

	// Obtain preferred terms for events.
	// Apply optional pathway filters.
 	MATCH (tEvent:Term)<-[rEvent:PT]-(cEvent:Code{SAB:'REACTOME'})<-[:CODE]-(pEvent)-[:isa{SAB:'REACTOME'}]->(pEventType:Concept)-[:CODE]->	(cEventType:Code{SAB:'REACTOME_VS'})-[rEventType:PT]->(tEventType:Term)
	WHERE CASE
		WHEN eventtypes[0]<>'' THEN ANY (eventtype IN eventtypes WHERE toLower(tEventType.name)=toLower(eventtype))
		ELSE toLower(tEventType.name) IN ['toplevelpathway','pathway'] END
	AND CASE
		WHEN pathwayid<>'' THEN cEvent.CODE=pathwayid ELSE 1=1 END
	AND CASE
		WHEN pathwayname<>'' THEN tEvent.name STARTS WITH pathwayname ELSE 1=1 END
	AND rEvent.CUI=pEvent.CUI
	RETURN cEvent.CODE AS EventCode, tEvent.name AS EventName, tEventType.name AS EventType
}

// Collect for response.
// Order events.
WITH EventType,EventName,EventCode,{type:EventType, code:EventCode,description:EventName} AS event
ORDER BY EventType DESC, EventName
// Collect events.
WITH COLLECT(DISTINCT event) AS events,COUNT(DISTINCT event) AS EventCount
//WITH COLLECT(DISTINCT {count:EventCount,events:events}) AS events
RETURN {count:EventCount,events:events} AS response


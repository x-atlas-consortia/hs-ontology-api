#!/bin/bash
##########
# Test script for hs-ontology-api integration with UBKG API
##########


set -e
set -u
###########
# Help function
##########
Help()
{
   # Display Help
   echo ""
   echo "****************************************"
   echo "HELP: hs-ontology-api API test script"
   echo
   echo "Syntax: ./test_api.sh [-option]..."
   echo "option"
   echo "-v     test environment: l (local), d (DEV), or p (PROD)"
}

########################################################################
# function to test the exact HTTP code and some characteristic of the
# JSON body of the response.
# When $1 is not blank, is will be used to see if it exactly matches
# the returned JSON body.
# When $1 is blank, $4 will be used to see if the JSON body is at
# least that length.
########################################################################
evaluate_JSON_body()
{
    ENDPOINT=$1
    EXPECTED_HTTP_RESPONSE_CODE=$2
    EXPECTED_JSON=$3

    # If we're not doing an exact match on the JSON, then we should be
    # doing a test that the length of the returned JSON is at least as
    # long as expected.
    if [[ "$#" -gt 3 ]]; then
	EXPECTED_JSON_LENGTH=$4
    else
	EXPECTED_JSON_LENGTH=0
    fi

    # Execute the endpoint, and save the response + response code to a
    # string that can be split apart.
    CURL_OUTPUT=$(curl --request GET \
		       --url "${UBKG_URL}${ENDPOINT}" \
		       --header "Content-Type: application/json" \
		       --silent \
		       --write-out "-_-_-_->http_code=%{http_code}")
    HTTP_RESPONSE_CODE=$(echo ${CURL_OUTPUT} | sed 's/.*-_-_-_->http_code=//')
    RESPONSE_JSON=$(echo ${CURL_OUTPUT} | sed 's/.-_-_-_->http_code=.*//')
    JSON_LENGTH=$(echo $RESPONSE_JSON | wc --chars)

    # Evaluate the result, either for an exact match or a minimum length JSON body
    if [[ "$HTTP_RESPONSE_CODE" != "$EXPECTED_HTTP_RESPONSE_CODE" ]]; then
	echo "FAILED. Got $HTTP_RESPONSE_CODE response when expecting $EXPECTED_HTTP_RESPONSE_CODE"
    else
	if [[ -n "$EXPECTED_JSON" && "$RESPONSE_JSON" != "$EXPECTED_JSON" ]]; then
	    echo "FAILED. Response JSON does not match expected JSON."
	elif [[ -n $JSON_LENGTH && $JSON_LENGTH -lt $EXPECTED_JSON_LENGTH ]]; then
	    echo "FAILED. Response JSON $JSON_LENGTH chars is shorter than expected length of $EXPECTED_JSON_LENGTH."
	else
	    echo "SUCCEEDED. Response HTTP code and JSON match expectations."
	fi
    fi
    echo
}

#####
# Get options
while getopts ":hv:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      v) # environment
         env=$OPTARG;;
      \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

# Check for environment parameter.
: ${env:?Missing environment parameter (-v). Run this script with -h for options.}

# Environment URLs.
UBKG_URL_PROD=https://ontology.api.hubmapconsortium.org
UBKG_URL_DEV=https://ontology-api.dev.hubmapconsortium.org
UBKG_URL_LOCAL=http://127.0.0.1:5002

# Map to selected API environment.
case "$env" in
  l) # local
    UBKG_URL="${UBKG_URL:-$UBKG_URL_LOCAL}";;
  d) # DEV
    UBKG_URL="${UBKG_URL:-$UBKG_URL_DEV}";;
  p) # PROD
    UBKG_URL="${UBKG_URL:-$UBKG_URL_PROD}";;
  \?) # default to local machine
    UBKG_URL="${UBKG_URL:-$UBKG_URL_LOCAL}";;

esac

echo "Using UBKG at: ${UBKG_URL}"
# $ ./test_api.sh
# Using UBKG at: https://ontology-api.dev.hubmapconsortium.org
# $ (export UBKG_URL=http://127.0.0.1:5002; ./test_api.sh)
# Using UBKG at: http://127.0.0.1:5002

echo "assayname_POST..."
curl --request POST \
 --url "${UBKG_URL}/assayname" \
 --header "Content-Type: application/json" \
 --data '{"name": "bulk-RNA"}'
echo

echo "assaytype GET"
curl --request GET \
 --url "${UBKG_URL}/assaytype?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo


echo "assaytype/<name> GET"
curl --request GET \
 --url "${UBKG_URL}/assaytype/bulk-RNA?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "datasets GET"
curl --request GET \
 --url "${UBKG_URL}/datasets?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "organs GET for HUBMAP"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "organs GET for SENNET"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=SENNET" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "organs/by-code GET"
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "relationships/gene GET..."
curl --request GET \
 --url "${UBKG_URL}/relationships/gene/MMRN1" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "valueset GET..."
curl --request GET \
 --url "${UBKG_URL}/valueset?child_sabs=OBI&parent_sab=HUBMAP&parent_code=C001000" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Test for gene_list endpoint
echo "genes-info GET"
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=1&genes_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "genes-info GET last page"
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=last&genes_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "genes-info GET starts_with B"
curl --request GET \
 --url "${UBKG_URL}/genes-info?genes_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Test for genes endpoint.
echo "genes GET for MMRN1"
curl --request GET \
 --url "${UBKG_URL}/genes/MMRN1" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Test for proteins-info endpoint.
echo "proteins-info GET"
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=1&proteins_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "proteins-info GET last page"
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=last&proteins_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "proteins-info GET starts_with B"
curl --request GET \
 --url "${UBKG_URL}/proteins-info?proteins_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" |cut -c1-60
echo
# Test for proteins endpoint.
echo "proteins GET for MMRN1_HUMAN"
curl --request GET \
 --url "${UBKG_URL}/proteins/MMRN1_HUMAN" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Test for celltypes list.
echo "celltypes-info GET"
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=1&cell_types_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "celltypes-info GET last page"
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=last&cell_types_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "celltypes-info GET starts_with B"
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?cell_types_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" |cut -c1-60
echo
# Test for proteins endpoint.
echo "celltypes GET for 0002138"
curl --request GET \
 --url "${UBKG_URL}/celltypes/0002138" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "SENNET source types"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C020076&child_sabs=SENNET" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "SENNET sample categories"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C050020&child_sabs=SENNET" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "SENNET entities"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C000012&child_sabs=SENNET" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-descriptions"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-descriptions/acquisition_instrument_model"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-descriptions/acquisition_instrument_model?test=X"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?test=X" \
 --header "Content-Type: application/json"
echo

echo "field-descriptions/acquisition_instrument_model?source=X"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?source=X" \
 --header "Content-Type: application/json"
echo

echo "field-descriptions/acquisition_instrument_model?source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types/acquisition_instrument_model"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types/acquisition_instrument_model?test=x"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?test=x" \
 --header "Content-Type: application/json"
echo

echo "field-types/acquisition_instrument_model?mapping_source=X"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?mapping_source=X" \
 --header "Content-Type: application/json"
echo

echo "field-types/acquisition_instrument_model?mapping_source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?mapping_source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types/acquisition_instrument_model?type_source=X"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type_source=X" \
 --header "Content-Type: application/json"
echo

echo "field-types/acquisition_instrument_model?type_source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type_source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types/acquisition_instrument_model?type=X"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type=X" \
 --header "Content-Type: application/json"
echo

echo "field-types/acquisition_instrument_model?type=string"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type=string" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types-info"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types-info" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types-info?test=x"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-types-info?test=x" \
 --header "Content-Type: application/json"
echo

echo "field-types-info?type_source=x"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-types-info?type_source=x" \
 --header "Content-Type: application/json"
echo

echo "field-types-info?type_source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types-info?type_source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model?test=X"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-assays?test=X" \
 --header "Content-Type: application/json"
echo

echo "field-assays?assay_identifier=X"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-assays?assay_identifier=X" \
 --header "Content-Type: application/json"
echo

echo "field-assays?assay_identifier=snRNAseq"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays?assay_identifier=snRNAseq" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model?assay_identifier=snRNAseq"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model?assay_identifier=snRNAseq" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays?data_type=X"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-assays?data_type=X" \
 --header "Content-Type: application/json"
echo

echo "field-assays?data_type=seqFISH"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays?data_type=seqFISH" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model?data_type=seqFISH"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model?data_type=seqFISH" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays?dataset_type=X"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-assays?dataset_type=x" \
 --header "Content-Type: application/json"
echo

echo "field-assays?dataset_type=RNAseq"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays?dataset_type=RNAseq" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model?dataset_type=RNAseq"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model?dataset_type=RNAseq" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities?test=X"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-entities?test=X" \
 --header "Content-Type: application/json"
echo

echo "field-entities/umi_offset"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities/umi_offset?source=x"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset?source=x" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities/umi_offset?source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset?source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities/umi_offset?entity=x"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset?entity=x" \
 --header "Content-Type: application/json"
echo

echo "field-entities/umi_offset?entity=dataset"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset?entity=dataset" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-schemas"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-schemas?test=x"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?test=x" \
 --header "Content-Type: application/json"
echo

echo "field-schemas/acquisition_instrument_model"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas/acquisition_instrument_model" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-schemas/acquisition_instrument_model?source=x"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?source=x" \
 --header "Content-Type: application/json"
echo

echo "field-schemas/acquisition_instrument_model?source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-schemas/acquisition_instrument_model?schema=x"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?schema=x" \
 --header "Content-Type: application/json"
echo

echo "field-schemas/acquisition_instrument_model?schema=imc3d"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?schema=imc3d" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Develop tests for the following endpoints.
# Snatch reasonable arguments from
# https://smart-api.info/ui/96e5b5c0b0efeef5b93ea98ac2794837/#/
#

echo "/concepts/paths/subgraph expecting HTTP 200 response"
evaluate_JSON_body \
    '/concepts/paths/subgraph?sab=SNOMEDCT_US&rel=isa&skip=0&limit=10' \
    '200' \
    '' \
    8077

# /concepts/{concept_id}/paths/expand - ubkg-api

echo "/concepts/C0006142/paths/expand?sab=SNOMEDCT_US&rel=isa&maxdepth=1 expecting HTTP 200 response"
evaluate_JSON_body \
    '/concepts/C0006142/paths/expand?sab=SNOMEDCT_US&rel=isa&maxdepth=1' \
    '200' \
    '' \
    540107

echo "/concepts/C0006142/paths/trees?sab=SNOMEDCT_US&rel=isa&maxdepth=0 expecting HTTP 200 response"
evaluate_JSON_body \
    '/concepts/C0006142/paths/trees?sab=SNOMEDCT_US&rel=isa&maxdepth=0' \
    '200' \
    '' \
    48172

echo "/concepts/C2720507/nodobjects expecting HTTP 200 response"
evaluate_JSON_body \
    '/concepts/C2720507/nodeobjects' \
    '200' \
    '{"nodeobjects":[{"node":{"codes":[{"codeid":"MTH:NOCODE","sab":"MTH","terms":[{"name":"SNOMED CT Concept (SNOMED RT+CTV3)","tty":"PN"}]},{"codeid":"SNOMEDCT_US:138875005","sab":"SNOMEDCT_US","terms":[{"name":"SNOMED CT has been created by combining SNOMED RT and a computer-based nomenclature and classification known as Read Codes Version 3, which was created on behalf of the U.K. Department of Health.","tty":"SY"},{"name":"\u00a9 2002-2023 International Health Terminology Standards Development Organisation (IHTSDO). All rights reserved. SNOMED CT\u00ae, was originally created by The College of American Pathologists. \"SNOMED\" and \"SNOMED CT\" are registered trademarks of the IHTSDO.","tty":"SY"},{"name":"SNOMED CT Concept (SNOMED RT+CTV3)","tty":"FN"},{"name":"SNOMED CT Concept","tty":"PT"}]},{"codeid":"SRC:V-SNOMEDCT_US","sab":"SRC","terms":[{"name":"US Edition of SNOMED CT","tty":"RPT"},{"name":"SNOMED CT Concept","tty":"RHT"},{"name":"SNOMED CT, US Edition","tty":"SSN"},{"name":"SNOMEDCT_US","tty":"RAB"}]}],"cui":"C2720507","definitions":[],"pref_term":"SNOMED CT Concept (SNOMED RT+CTV3)","semantic_types":[{"def":"A conceptual entity resulting from human endeavor. Concepts assigned to this type generally refer to information created by humans for some purpose.","stn":"A2.4","sty":"Intellectual Product","tui":"T170"}]}}]}'


echo "/concepts/C2720507/paths/shortestpath/C1272753?sab=SNOMEDCT_US&rel=isa expecting HTTP 200 response"
evaluate_JSON_body \
    '/concepts/C2720507/paths/shortestpath/C1272753?sab=SNOMEDCT_US&rel=isa' \
    '200' \
    '' \
    1385

echo "/database/server expecting HTTP 200 response"
evaluate_JSON_body \
    '/database/server'\
    '200' \
    '{"edition":"community","version":"5.11.0"}'

echo "/node-types expecting HTTP 200 response"
evaluate_JSON_body \
    '/node-types' \
    '200' \
    '{"node_types":["Code","Concept","Definition","Semantic","Term"]}'

echo "/node-types/Code/counts?sab=MSH expecting HTTP 200 response"
evaluate_JSON_body \
    '/node-types/Code/counts?sab=MSH' \
    '200' \
    '{"node_types":[{"node_type":{"count":5088308,"label":"Code"}}],"total_count":5088308}'

echo "/node-types/Code/counts-by-sab?sab=MSH expecting HTTP 200 response"
evaluate_JSON_body \
    '/node-types/Code/counts-by-sab?sab=MSH' \
    '200' \
    '{"node_types":[{"node_type":{"count":353698,"label":"Code","sabs":[{"count":353698,"sab":"MSH"}]}}],"total_count":353698}'

echo "/property-types expecting HTTP 200 response"
evaluate_JSON_body \
    '/property-types' \
    '200' \
    '{"property_types":["ATUI","CODE","CUI","CodeID","DEF","SAB","STN","TUI","evidence_class","lowerbound","name","upperbound","value"]}'

echo "/relationship-types expecting HTTP 200 response"
evaluate_JSON_body \
    '/relationship-types' \
    '200' \
    '' \
    43755

echo "/sabs expecting HTTP 200 response"
evaluate_JSON_body \
    '/sabs' \
    '200' \
    '' \
    2238010

echo "/sabs/codes/counts expecting HTTP 200 response"
evaluate_JSON_body \
    '/sabs/codes/counts' \
    '200' \
    '' \
    44855

echo "/sabs/MSH/codes/counts expecting HTTP 200 response"
evaluate_JSON_body \
    '/sabs/MSH/codes/counts' \
    '200' \
    '{"sabs":[{"count":353698,"position":1,"sab":"MSH"}]}'

echo "/sabs/MSH/codes/details expecting HTTP 200 response"
evaluate_JSON_body \
    '/sabs/MSH/codes/details' \
    '200' \
    '' \
    177515

echo "/sabs/MSH/term-types expecting HTTP 200 response"
evaluate_JSON_body \
    '/sabs/MSH/term-types' \
    '200' \
    '{"sab":"MSH","term_types":["PM","N1","ET","DEV","DSV","MH","PEP","XQ","PXQ","QEV","TQ","QAB","PCE","NM","CE","HT","QSV","HS"]}'

echo "/semantics/semantic-types expecting HTTP 200 response"
evaluate_JSON_body \
    '/semantics/semantic-types' \
    '200' \
    '' \
    31214

echo "/semantics/semantic-types/T071 expecting HTTP 200 response"
evaluate_JSON_body \
    '/semantics/semantic-types/T071' \
    '200' \
    '{"semantic_types":[{"position":1,"semantic_type":{"def":"A broad type for grouping physical and conceptual entities.","stn":"A","sty":"Entity","tui":"T071"}}]}'

echo "/semantics/semantic-types/T071 expecting HTTP 200 response"
evaluate_JSON_body \
    '/semantics/semantic-types/T071/subtypes' \
    '200' \
    '' \
    20574
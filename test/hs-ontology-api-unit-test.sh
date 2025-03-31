#!/bin/bash
#########
# FULL UNIT TEST SCRIPT
# This script repeatedly calls endpoints of the ubkg-api in (one hopes) all possible scenarios,
# including for parameters. Use this to check validation of parameters.
# Use the environment test script to check for infrastructure features such as gateway, timeout, and
# payload size checks.
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
   echo "HELP: hs-ontology API unit test script"
   echo
   echo "Syntax: ./hs-ontology-api-unit-test.sh [-option]..."
   echo "option"
   echo "-v     test environment: l (local), d (DEV), or p (PROD)"
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

# output file
testout=hs-ontology-api-unit-test.out

echo "Using UBKG instance at: ${UBKG_URL}" | tee $testout
echo "For these tests, only first 60 characters of output from HTTP 200 returns displayed." | tee -a $testout
echo "To review response bodies in detail, call endpoints individually." | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

# $ ./test_api.sh
# Using UBKG at: https://ontology-api.dev.hubmapconsortium.org
# $ (export UBKG_URL=http://127.0.0.1:5002; ./test_api.sh)
# Using UBKG at: http://127.0.0.1:5002

echo "TESTS FOR: pathways/with-genes GET" | tee -a $testout
echo "SIGNATURE: /pathways/with-genes?geneids=<list>&pathwayid=<pathwayid>&pathwaynamestartswith=<string>&eventtypes=<list>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout
echo "1. /pathways/with-genes => valid; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /pathways/with-genes?geneids=EGFR => valid with gene; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?geneids=EGFR" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. /pathways/with-genes?geneids=EGFR,BRCA1 => valid with list of genes; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?geneids=EGFR,BRCA1" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "4. /pathways/with-genes?geneids=EGFR&geneids=BRCA1 => valid with list of genes; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?geneids=EGFR&geneids=BRCA1" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "5. /pathways/with-genes?pathwayid=R-HSA-74160 => valid parameter; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?pathwayid=R-HSA-74160" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "6. /pathways/with-genes?pathwayname-startswith=AT => valid parameter; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?pathwayname-startswith=AT" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "7. /pathways/with-genes?eventtypes=reaction => valid parameter; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?eventtypes=reaction" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "8. /pathways/with-genes?eventtypes=x => invalid parameter value; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?eventtypes=x" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "9. /pathways/with-genes?geneids=x => should return 404" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?geneids=x" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "10. /pathways/with-genes?test=x => should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes?test=x" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: assayclasses GET" | tee -a $testout
echo "SIGNATURE: /assayclasses?application_context=<context>&process_state=<process_state>&provide_hiearchy_info=<true,false>&provide_measurement_assay_codes=<true,false>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout
echo "1. /assayclasses?application_context=x => invalid application context; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses?application_context=HUBMAPx" \
 --header "Accept: application/json" | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout
echo "2. /assayclasses => missing application context; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses?" \
 --header "Accept: application/json" | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. /assayclasses => invalid parameter; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses?application_context=HUBMAP&process_state=x" \
 --header "Accept: application/json" | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "4. /assayclasses => valid, all; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses?application_context=HUBMAP" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "5. /assayclasses => valid, all, primary; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses?application_context=HUBMAP&process_state=primary" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "6. /assayclasses/AFX => invalid assayclass; should return 404" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses/AFX?application_context=HUBMAP" \
--header "Accept: application/json" | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "7. /assayclasses/non-DCWG primary AF => valid assayclass; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses/non-DCWG%20primary%20AF?application_context=HUBMAP" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "8. /assayclasses/C200001 => valid assayclass; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses/C200001?application_context=HUBMAP" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "9. /assayclasses/C200001 => invalid provide-hierarchy-info; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses/C200001?application_context=HUBMAP&provide-hierarchy-info=x" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "10. /assayclasses/C200001 => valid provide-hierarchy-info; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses/C200001?application_context=HUBMAP&provide-hierarchy-info=true" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "11. /assayclasses/C200001 => invalid provide-measurement-assay-codes should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses/C200001?application_context=HUBMAP&provide-measurement-assay-codes=x" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "12. /assayclasses/C200001 => valid provide-measurement-assay-codes; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses/C200001?application_context=HUBMAP&provide-measurement-assay-codes=true" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: dataset-types GET" | tee -a $testout
echo "SIGNATURE: /dataset-types?application_context" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /dataset-types?application_context=x => invalid application context; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/dataset-types?application_context=HUBMAPx" \
 --header "Accept: application/json" | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout


echo "2. /dataset-types => missing application context; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/dataset-types?" \
 --header "Accept: application/json" | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. /dataset-types?application_context=HUBMAP&is_externally_processed=mango => invalid parameter; should return custom 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/dataset-types?application_context=HUBMAP&is_externally_processed=mango" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo "4. /dataset-types?application_context=HUBMAP => valid; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/dataset-types?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo "5. /dataset-types?application_context=HUBMAP&is_externally_processed=false => valid; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/dataset-types?application_context=HUBMAP&is_externally_processed=true" \
 --header "Accept: application/json" | tee -a $testout


# dataset-types/<id> uses the same code as dataset-types
echo "TESTS FOR: dataset-types/<id> GET" | tee -a $testout
echo "SIGNATURE: /dataset-types/<id>?application_context" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /dataset-types/test?application_context=x => invalid dataset-type; should return custom 404" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/dataset-types/test?application_context=HUBMAPx" \
 --header "Accept: application/json" | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /dataset-types/2D Imaging Mass Cytometry?application_context=HUBMAP => valid; should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/dataset-types/2D%20Imaging%20Mass%20Cytometry?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo

echo "TESTS FOR: organs GET" | tee -a $testout
echo "SIGNATURE: /organs?application_context=<context>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /organs => missing application context; should return custom 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/organs" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /organs?application_context=HUBMAP => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. /organs?application_context=SENNET => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=SENNET" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: organs/by-code GET" | tee -a $testout
echo "SIGNATURE: /organs/by-code?application_context=<context>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/organs/by-code?application_context=HUBMAP => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: relationships/gene GET" | tee -a $testout
echo "SIGNATURE: /relationships/gene/<HGNC symbol>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "relationships/gene/MMRN1 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/relationships/gene/MMRN1" \
 --header "Content-Type: application/json"| cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: valueset GET" | tee -a $testout
echo "SIGNATURE: /valueset?child_sabs=<list of sabs.&parent_sab=<sab>&parent_code=<code>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/valueset?child_sabs=OBI&parent_sab=HUBMAP&parent_code=C000002 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/valueset?child_sabs=OBI&parent_sab=HUBMAP&parent_code=C000002" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: genes-info GET" | tee -a $testout
echo "SIGNATURE: /gene_list?page=<page>&genes_per_page=<number>&starts_with=<characters>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

# Test for genes-info endpoint
echo "1. /genes-info?page=1&genes_per_page=3 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=1&genes_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /genes-info?page=last&genes_per_page=3 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=last&genes_per_page=3" \
 --header "Content-Type: application/json"| cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. /genes-info?genes_per_page=3&starts_with=B => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/genes-info?genes_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

# Test for genes endpoint.
echo "TESTS FOR: genes GET" | tee -a $testout
echo "SIGNATURE: /genes/<HGNC symbol>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/genes/MMRN1 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/genes/MMRN1" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

# Test for proteins-info endpoint.
echo "TESTS FOR: proteins-info GET" | tee -a $testout
echo "SIGNATURE: /proteins_info?page=<page>&proteins_per_page=<number>&starts_with=<characters>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /proteins-info?page=1&proteins_per_page=3 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=1&proteins_per_page=3" \
 --header "Content-Type: application/json"| cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /proteins-info?page=last&proteins_per_page=3 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=last&proteins_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. /proteins-info?proteins_per_page=3&starts_with=B => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/proteins-info?proteins_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: proteins GET" | tee -a $testout
echo "SIGNATURE: /genes/<UniProtKB symbol>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

# Test for proteins endpoint.
echo "/proteins/MMRN1_HUMAN => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/proteins/MMRN1_HUMAN" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: celltypes-info GET" | tee -a $testout
echo "SIGNATURE: /celltypesinfo?page=<page>&cell_types_per_page=<number>&starts_with=<characters>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /celltypes-info?page=1&proteins_per_page=3 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=1&proteins_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /celltypes-info?page=last&proteins_per_page=3 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=last&proteins_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /celltypes-info?proteins_per_page=3&starts_with=B => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?proteins_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

# Test for celltypes endpoint.
echo "TESTS FOR: celltypes GET" | tee -a $testout
echo "SIGNATURE: /celltypesinfo/<CL code>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/celltypes/0002138 => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/celltypes/0002138" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TEST FOR: SENNET source types" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C020076&child_sabs=SENNET" \
 --header "Content-Type: application/json" | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TEST FOR: SENNET sample categories" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C050020&child_sabs=SENNET" \
 --header "Content-Type: application/json" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "TEST FOR: SENNET entities" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C000012&child_sabs=SENNET" \
 --header "Content-Type: application/json" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: field-descriptions GET" | tee -a $testout
echo "SIGNATURE: /field-descriptions/<field name>?source=<source?>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1./ field-descriptions => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-descriptions" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /field-descriptions/acquisition_instrument_model => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. /field-descriptions/acquisition_instrument_model?test=X => invalid parameter; should return custom 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?test=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "4. /field-descriptions/acquisition_instrument_model?source=X => invalid source; should return custom 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?source=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "5. field-descriptions/acquisition_instrument_model?source=HMFIELD = > should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: field-types GET" | tee -a $testout
echo "SIGNATURE: /field-types/<field name>?mapping_source=<source>&type_source=<source>&type=<type>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /field-types => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /field-types/acquisition_instrument_model => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model" \
 --header "Content-Type: application/json"  | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. field-types/acquisition_instrument_model?test=x => invalid parameter: should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?test=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "4. field-types/acquisition_instrument_model?mapping_source=X => invalid mapping source; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?mapping_source=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "5. field-types/acquisition_instrument_model?mapping_source=HMFIELD => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?mapping_source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "6. field-types/acquisition_instrument_model?type_source=X => invalid type_source; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type_source=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "7. field-types/acquisition_instrument_model?type_source=HMFIELD => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type_source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "8. field-types/acquisition_instrument_model?type=X => invalid type; should return 404" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "9. field-types/acquisition_instrument_model?type=string => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type=string" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: field-types-info GET" | tee -a $testout
echo "SIGNATURE: /field-types-info?type_source=<source>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /field-types-info => SHOULD RETURN 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types-info" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /field-types-info?test=x => invalid parameter; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types-info?test=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. /field-types-info?type_source=x => invalid type_source; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types-info?type_source=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "4. field-types-info?type_source=HMFIELD => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types-info?type_source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: field-assays GET" | tee -a $testout
echo "SIGNATURE: /field-assays/<assay_identifier>?assaytype=<assaytype>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /field-assays => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-assays" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /field-assays/acquisition_instrument_model => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "3. field-assays/acquisition_instrument_model?test=X => invalid parameter; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model?test=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "4. /field-assays?assaytype=X => no results; should return 404" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-assays?assaytype=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "5. /field-assays?assaytype=snRNAseq => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-assays?assaytype=snRNAseq" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: field-entities GET" | tee -a $testout
echo "SIGNATURE: /field-entities/<field_name>?source=<source>&entity=<entity>&application_context=<context>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /field-entities => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-entities" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /field-entities?test=X => invalid parameter; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-entities?test=X" \
 --header "Content-Type: application/json"
echo

echo "3. /field-entities/acquisition_instrument_model => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "4. /field-entities/acquisition_instrument_model?source=x => invalid source; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model?source=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "5. /field-entities/acquisition_instrument_model?source=HMFIELD => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model?source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "6. /field-entities/acquisition_instrument_model?entity=x => no results; should return 404" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model?entity=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "7. /field-entities/acquisition_instrument_model?entity=dataset => should return 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model?entity=dataset" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "TESTS FOR: field-schemas GET" | tee -a $testout
echo "SIGNATURE: /field-entities/<field_name>?source=<source>&schema=<schema>" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "1. /field-schemas => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-schemas" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "2. /field-schemas?test=x => invalid parameter; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-schemas?test=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout


echo "3. /field-schemas/acquisition_instrument_model => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-schemas/acquisition_instrument_model" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "4. /field-schemas/acquisition_instrument_model?source=x => invalid parameter value; should return 400" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-schemas?source=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "5. /field-schemas/acquisition_instrument_model?source=HMFIELD => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-schemas?source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "6. /field-schemas/acquisition_instrument_model?schema=x => no results; should return 404" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-schemas?schema=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "7. /field-schemas/acquisition_instrument_model?schema=imc3d => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-schemas?schema=imc3d" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout
echo

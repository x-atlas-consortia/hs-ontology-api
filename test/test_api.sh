#!/bin/bash
##########
# Test script for hs-ontology API
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
   echo "HELP: hs-ontology API test script"
   echo
   echo "Syntax: ./test_api.sh [-option]..."
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

echo "Using UBKG at: ${UBKG_URL}" | tee test.out
echo "For these tests, only first 60 characters of output from HTTP 200 returns displayed." | tee -a test.out
echo "To review response bodies in detail, call endpoints individually." | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

# $ ./test_api.sh
# Using UBKG at: https://ontology-api.dev.hubmapconsortium.org
# $ (export UBKG_URL=http://127.0.0.1:5002; ./test_api.sh)
# Using UBKG at: http://127.0.0.1:5002

#--------------------------------------------
echo "TESTS FOR: assayname POST" | tee -a test.out
echo "SIGNATURE: /assayname" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "/assayname_POST with bulk-RNA => should return 200" | tee -a test.out
curl --request POST \
 --url "${UBKG_URL}/assayname" \
 --header "Content-Type: application/json" \
 --data '{"name": "bulk-RNA"}' | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: assaytypes GET" | tee -a test.out
echo "SIGNATURE: /assaytypes?application_context=<context>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out
echo "/assaytype?application_context=HUBMAP GET => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assaytype?application_context=HUBMAP" \
 --header "Accept: application/json"| cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out


echo "TESTS FOR: assaytypes GET" | tee -a test.out
echo "SIGNATURE: /assaytypes/<data_type name>?application_context=<context>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out
echo "/assaytypes/bulk-RNA?application_context=HUBMAP => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assaytype/bulk-RNA?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: assayclasses GET" | tee -a test.out
echo "SIGNATURE: /assayclassed?application_context=<context>&is_primary=<is_primary>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out
echo "1. /assaytypes?application_context=x => invalid application context; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assayclass/?application_context=HUBMAPx" \
 --header "Accept: application/json" | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out
echo "2. /assaytypes => missing application context; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assaytype?application_context=HUBMAP" \
 --header "Accept: application/json" | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "3. /assaytypes => invalid parameter; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assaytype?application_context=HUBMAP&is_primary=x" \
 --header "Accept: application/json" | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. /assaytypes => valid, all; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assaytype?application_context=HUBMAP" \
--header "Accept: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. /assaytypes => valid, all, primary; should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assaytype?application_context=HUBMAP&is_primary=true" \
--header "Accept: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. /assaytypes/AFX => invalid assaytype; should return 404" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assaytype/AFX?application_context=HUBMAP" \
--header "Accept: application/json" | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. /assaytypes/AF => valid assaytype; should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/assaytype/AF?application_context=HUBMAP" \
--header "Accept: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: organs GET" | tee -a test.out
echo "SIGNATURE: /organs?application_context=<context>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1. /organs => missing application context; should return custom 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/organs" \
 --header "Accept: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /organs?application_context=HUBMAP => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "3. /organs?application_context=SENNET => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=SENNET" \
 --header "Accept: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: organs/by-code GET" | tee -a test.out
echo "SIGNATURE: /organs/by-code?application_context=<context>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "/organs/by-code?application_context=HUBMAP => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: relationships/gene GET" | tee -a test.out
echo "SIGNATURE: /relationships/gene/<HGNC symbol>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "relationships/gene/MMRN1 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/relationships/gene/MMRN1" \
 --header "Content-Type: application/json"| cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: valueset GET" | tee -a test.out
echo "SIGNATURE: /valueset?child_sabs=<list of sabs.&parent_sab=<sab>&parent_code=<code>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "/valueset?child_sabs=OBI&parent_sab=HUBMAP&parent_code=C000002 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/valueset?child_sabs=OBI&parent_sab=HUBMAP&parent_code=C000002" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: genes-info GET" | tee -a test.out
echo "SIGNATURE: /gene_list?page=<page>&genes_per_page=<number>&starts_with=<characters>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

# Test for genes-info endpoint
echo "1. /genes-info?page=1&genes_per_page=3 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=1&genes_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /genes-info?page=last&genes_per_page=3 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=last&genes_per_page=3" \
 --header "Content-Type: application/json"| cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "3. /genes-info?genes_per_page=3&starts_with=B => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/genes-info?genes_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

# Test for genes endpoint.
echo "TESTS FOR: genes GET" | tee -a test.out
echo "SIGNATURE: /genes/<HGNC symbol>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "/genes/MMRN1 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/genes/MMRN1" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

# Test for proteins-info endpoint.
echo "TESTS FOR: proteins-info GET" | tee -a test.out
echo "SIGNATURE: /proteins_info?page=<page>&proteins_per_page=<number>&starts_with=<characters>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1. /proteins-info?page=1&proteins_per_page=3 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=1&proteins_per_page=3" \
 --header "Content-Type: application/json"| cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /proteins-info?page=last&proteins_per_page=3 => should return 200" | tee -a test.out
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=last&proteins_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "3. /proteins-info?proteins_per_page=3&starts_with=B => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/proteins-info?proteins_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: proteins GET" | tee -a test.out
echo "SIGNATURE: /genes/<UniProtKB symbol>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

# Test for proteins endpoint.
echo "/proteins/MMRN1_HUMAN => should return 200" | tee -a test.out
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/proteins/MMRN1_HUMAN" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: celltypes-info GET" | tee -a test.out
echo "SIGNATURE: /celltypesinfo?page=<page>&cell_types_per_page=<number>&starts_with=<characters>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1. /celltypes-info?page=1&proteins_per_page=3 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=1&proteins_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /celltypes-info?page=last&proteins_per_page=3 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=last&proteins_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /celltypes-info?proteins_per_page=3&starts_with=B => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?proteins_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

# Test for celltypes endpoint.
echo "TESTS FOR: celltypes GET" | tee -a test.out
echo "SIGNATURE: /celltypesinfo/<CL code>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "/celltypes/0002138 => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/celltypes/0002138" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TEST FOR: SENNET source types" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C020076&child_sabs=SENNET" \
 --header "Content-Type: application/json" | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TEST FOR: SENNET sample categories" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C050020&child_sabs=SENNET" \
 --header "Content-Type: application/json" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "TEST FOR: SENNET entities" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C000012&child_sabs=SENNET" \
 --header "Content-Type: application/json" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: field-descriptions GET" | tee -a test.out
echo "SIGNATURE: /field-descriptions/<field name>?source=<source?>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1./ field-descriptions => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-descriptions" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /field-descriptions/acquisition_instrument_model => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "3. /field-descriptions/acquisition_instrument_model?test=X => invalid parameter; should return custom 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?test=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. /field-descriptions/acquisition_instrument_model?source=X => invalid source; should return custom 400" | tee -a test.out
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?source=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "5. field-descriptions/acquisition_instrument_model?source=HMFIELD = > should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: field-types GET" | tee -a test.out
echo "SIGNATURE: /field-types/<field name>?mapping_source=<source>&type_source=<source>&type=<type>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1. /field-types => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /field-types/acquisition_instrument_model => should return 200" | tee -a test.out
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model" \
 --header "Content-Type: application/json"  | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "3. field-types/acquisition_instrument_model?test=x => invalid parameter: should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?test=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. field-types/acquisition_instrument_model?mapping_source=X => invalid mapping source; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?mapping_source=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "5. field-types/acquisition_instrument_model?mapping_source=HMFIELD => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?mapping_source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "6. field-types/acquisition_instrument_model?type_source=X => invalid type_source; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type_source=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "7. field-types/acquisition_instrument_model?type_source=HMFIELD => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type_source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "8. field-types/acquisition_instrument_model?type=X => invalid type; should return 404" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "9. field-types/acquisition_instrument_model?type=string => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type=string" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: field-types-info GET" | tee -a test.out
echo "SIGNATURE: /field-types-info?type_source=<source>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1. /field-types-info => SHOULD RETURN 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types-info" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /field-types-info?test=x => invalid parameter; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types-info?test=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "3. /field-types-info?type_source=x => invalid type_source; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types-info?type_source=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. field-types-info?type_source=HMFIELD => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-types-info?type_source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: field-assays GET" | tee -a test.out
echo "SIGNATURE: /field-assays/<assay_identifier>?assaytype=<assaytype>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1. /field-assays => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-assays" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /field-assays/acquisition_instrument_model => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "3. field-assays/acquisition_instrument_model?test=X => invalid parameter; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model?test=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. /field-assays?assaytype=X => no results; should return 404" | tee -a test.out
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-assays?assaytype=X" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "5. /field-assays?assaytype=snRNAseq => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-assays?assaytype=snRNAseq" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: field-entities GET" | tee -a test.out
echo "SIGNATURE: /field-entities/<field_name>?source=<source>&entity=<entity>&application_context=<context>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1. /field-entities => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-entities" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /field-entities?test=X => invalid parameter; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-entities?test=X" \
 --header "Content-Type: application/json"
echo

echo "3. /field-entities/acquisition_instrument_model => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. /field-entities/acquisition_instrument_model?source=x => invalid source; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model?source=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "5. /field-entities/acquisition_instrument_model?source=HMFIELD => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model?source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "6. /field-entities/acquisition_instrument_model?entity=x => no results; should return 404" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model?entity=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "7. /field-entities/acquisition_instrument_model?entity=dataset => should return 200"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities/acquisition_instrument_model?entity=dataset" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "TESTS FOR: field-schemas GET" | tee -a test.out
echo "SIGNATURE: /field-entities/<field_name>?source=<source>&schema=<schema>" | tee -a test.out
echo | tee -a test.out
echo | tee -a test.out

echo "1. /field-schemas => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-schemas" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "2. /field-schemas?test=x => invalid parameter; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-schemas?test=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out


echo "3. /field-schemas/acquisition_instrument_model => should return 200" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-schemas/acquisition_instrument_model" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "4. /field-schemas/acquisition_instrument_model?source=x => invalid parameter value; should return 400" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-schemas?source=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "5. /field-schemas/acquisition_instrument_model?source=HMFIELD => should return 200" | tee -a test.out
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?source=HMFIELD" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "6. /field-schemas/acquisition_instrument_model?schema=x => no results; should return 404" | tee -a test.out
curl --request GET \
 --url "${UBKG_URL}/field-schemas?schema=x" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out

echo "7. /field-schemas/acquisition_instrument_model?schema=imc3d => should return 200" | tee -a test.out
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?schema=imc3d" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a test.out
echo
echo | tee -a test.out
echo | tee -a test.out
echo

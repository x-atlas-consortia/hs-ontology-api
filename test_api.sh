#!/bin/bash
##########
# Test script for UBKG API
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
   echo "HELP: UBKG API test script"
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
 --header "Accept: application/json"
echo

echo "assaytype/<name> GET"
curl --request GET \
 --url "${UBKG_URL}/assaytype/bulk-RNA?application_context=HUBMAP" \
 --header "Accept: application/json"
echo

echo "datasets GET"
curl --request GET \
 --url "${UBKG_URL}/datasets?application_context=HUBMAP" \
 --header "Accept: application/json"
echo

echo "organs GET for HUBMAP"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
 --header "Accept: application/json"
echo

echo "organs GET for SENNET"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=SENNET" \
 --header "Accept: application/json"
echo

echo "organs/by-code GET"
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Accept: application/json"
echo

echo "relationships/gene GET..."
curl --request GET \
 --url "${UBKG_URL}/relationships/gene/MMRN1" \
 --header "Content-Type: application/json"
echo

echo "valueset GET..."
curl --request GET \
 --url "${UBKG_URL}/valueset?child_sabs=OBI&parent_sab=HUBMAP&parent_code=C001000" \
 --header "Content-Type: application/json"
echo

# Test for gene_list endpoint
echo "gene_list GET"
curl --request GET \
 --url "${UBKG_URL}/gene_list?page=1&genesperpage=3" \
 --header "Content-Type: application/json"
echo
echo "gene_list GET last page"
curl --request GET \
 --url "${UBKG_URL}/gene_list?page=last&genesperpage=3" \
 --header "Content-Type: application/json"
echo

# Test for gene_detail endpoint.
echo "gene_detail GET for MMRN1"
curl --request GET \
 --url "${UBKG_URL}/gene_detail?id=MMRN1" \
 --header "Content-Type: application/json"
echo

echo "SENNET source types"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C020076&child_sabs=SENNET" \
 --header "Content-Type: application/json"
echo

echo "SENNET sample categories"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C050020&child_sabs=SENNET" \
 --header "Content-Type: application/json"
echo

echo "SENNET entities"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C000012&child_sabs=SENNET" \
 --header "Content-Type: application/json"
echo
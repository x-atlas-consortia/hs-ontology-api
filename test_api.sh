#!/bin/bash
set -e
set -u

UBKG_URL_PROD=https://ontology.api.hubmapconsortium.org
UBKG_URL_DEV=https://ontology-api.dev.hubmapconsortium.org
UBKG_URL_LOCAL=http://127.0.0.1:5002
UBKG_URL="${UBKG_URL:-$UBKG_URL_LOCAL}"
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

# JAS Sept 2023 - Removed duplicate calls.

# JAS Sept 2023 - Test for genes endpoint.
echo "genes POST"
curl --request POST \
 --url "${UBKG_URL}/genes" \
 --header "Content-Type: application/json" \
 --data '{"ids": ["60","MMRN1","FANCS"]}'
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
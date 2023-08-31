#!/bin/bash
set -e
set -u

UBKG_URL_PROD=https://ontology.api.hubmapconsortium.org
UBKG_URL_DEV=https://ontology-api.dev.hubmapconsortium.org
UBKG_URL_LOCAL=http://127.0.0.1:5002
UBKG_URL=$UBKG_URL_LOCAL

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

echo "organs GET"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
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
 --url "${UBKG_URL}/valueset?child_sabs=HGNC&child_sabs=OBI&parent_sab=HUBMAP&parent_code=C001000" \
 --header "Content-Type: application/json"
echo

# Two calls used by the HuBMAP ingest-ui
echo "Used by ingest-ui: assaytype?application_context=HUBMAP GET..."
curl --request GET \
 --url "${UBKG_URL}/assaytype?application_context=HUBMAP&primary=true" \
 --header "Content-Type: application/json"
echo

echo "Used by ingest-ui: organs/by-code?application_context=HUBMAP GET..."
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Content-Type: application/json"
echo

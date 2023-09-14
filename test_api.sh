#!/bin/bash
set -e
set -u

UBKG_URL_PROD=https://ontology.api.hubmapconsortium.org
UBKG_URL_DEV=https://ontology-api.dev.hubmapconsortium.org
UBKG_URL_LOCAL=http://127.0.0.1:5002
UBKG_URL="${UBKG_URL:-$UBKG_URL_DEV}"
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

# https://github.com/x-atlas-consortia/hs-ontology-api/pull/26#pullrequestreview-1620865736
# Expected results:
# - One instance of Skin, mapped to UBERON 0002097. (This is the current case in production;
#   however, as the new code modifies the original case statement that de-duplicated skin,
#   this should be tested, too.)
# - One instance of Muscle, mapped to UBERON 0005090.
echo "organs hs-ontology-api pull-26 test"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=SENNET" \
 --header "Accept: application/json"
echo

# This endpoint should also be tested against the HUBMAP application context. HuBMAP's organ list
# does not include muscle, but does include skin, so testing should confirm that the call to the
# HuBMAP context returns only one entry for skin.
echo "organs hs-ontology-api pull-26 test"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
 --header "Accept: application/json"
echo

#!/bin/bash
set -e
set -u

INGESTAPI_URL_PROD=https://ingest.api.hubmapconsortium.org
INGESTAPI_URL_DEV=https://ingest-api.dev.hubmapconsortium.org
INGESTAPI_URL_TEST=https://ingest-api.test.hubmapconsortium.org
INGESTAPI_URL_LOCAL=http://localhost:8484
INGESTAPI_URL=$INGESTAPI_URL_DEV

UBKG_URL_PROD=https://ontology.api.hubmapconsortium.org
UBKG_URL_DEV=https://ontology-api.dev.hubmapconsortium.org
UBKG_URL_LOCAL=http://127.0.0.1:5002
UBKG_URL=$UBKG_URL_LOCAL

SEARCH_URL_DEV=https://search-api.dev.hubmapconsortium.org
SEARCH_URL_TEST=https://search-api.test.hubmapconsortium.org
SEARCH_URL=$SEARCH_URL_DEV

UUID_URL_DEV=https://uuid-api.dev.hubmapconsortium.org
UUID_URL=$UUID_URL_DEV


# To get the BEARER_TOKEN, login through the UI (https://ingest.hubmapconsortium.org/) to get the credentials...
# In Firefox open 'Tools > Browser Tools > Web Developer Tools'.
# Click on "Storage" then the dropdown for "Local Storage" and then the url,
# Applications use the "groups_token" from the returned information.
# UI times-out in 15 min so close the browser window, and the token will last for a day or so.
#
# Run this with....
# export TOKEN="xxx"; ./src/ubkg_api/test_api.sh

echo "datasets GET"
curl --request GET \
 --url "${UBKG_URL}/datasets?application_context=HUBMAP" \
 --header "Accept: application/json" \
 --header "Authorization: Bearer ${TOKEN}"
echo

echo "organs GET"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
 --header "Accept: application/json" \
 --header "Authorization: Bearer ${TOKEN}"
echo

echo "organs/by-code GET"
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Accept: application/json" \
 --header "Authorization: Bearer ${TOKEN}"
echo

echo "relationships/gene GET..."
curl --request GET \
 --url "${UBKG_URL}/relationships/gene/MMRN1" \
 --header "Content-Type: application/json" \
 --header "Authorization: Bearer ${TOKEN}"
echo

echo "valueset GET..."
curl --request GET \
 --url "${UBKG_URL}/valueset?child_sabs=HGNC&child_sabs=SNOMEDCT_US&parent_sab=HUBMAP&parent_code=C000530" \
 --header "Content-Type: application/json" \
 --header "Authorization: Bearer ${TOKEN}"
echo

# Two calls used by the HuBMAP ingest-ui
echo "Used by ingest-ui: assaytype?application_context=HUBMAP GET..."
curl --request GET \
 --url "${UBKG_URL}/assaytype?application_context=HUBMAP&primary=true" \
 --header "Content-Type: application/json" \
 --header "Authorization: Bearer ${TOKEN}"
echo

echo "Used by ingest-ui: organs/by-code?application_context=HUBMAP GET..."
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Content-Type: application/json" \
 --header "Authorization: Bearer ${TOKEN}"
echo

#!/bin/bash
set -e
set -u

ASSAYCLASS_URL_LOCAL=http://localhost:8181
ASSAYCLASS_URL=$ASSAYCLASS_URL_LOCAL


curl --request GET \
 --url "${ASSAYCLASS_URL}"
echo
echo


echo "Only the last one in the group should succeed..."
curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses" \
 --header "Accept: application/json"
echo

curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses?application_context=Wrong" \
 --header "Accept: application/json"
echo

curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses?application_context=HUBMAp" \
 --header "Accept: application/json"
echo
echo


echo "Only the last one in the group should succeed..."
curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses/C200010" \
 --header "Accept: application/json"
echo

curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses/xyzzy?application_context=NoMap" \
 --header "Accept: application/json"
echo

curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses/xyzzy?application_context=huBMAP" \
 --header "Accept: application/json"
echo

curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses/C200010?application_context=HUbmAP" \
 --header "Accept: application/json"
echo

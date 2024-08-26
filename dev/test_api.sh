#!/bin/bash
set -e
set -u

ASSAYCLASS_URL_LOCAL=http://localhost:8181
ASSAYCLASS_URL=$ASSAYCLASS_URL_LOCAL


curl --request GET \
 --url "${ASSAYCLASS_URL}"
echo


# Both endpoints require the application_context=HUBMAP parameter to be included, otherwise return a 400.
curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses" \
 --header "Accept: application/json"
echo

curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses?application_context=HUBMAP" \
 --header "Accept: application/json"
echo


curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses/C200010" \
 --header "Accept: application/json"
echo

curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses/xyzzy?application_context=HUBMAP" \
 --header "Accept: application/json"
echo

curl --request GET \
 --url "${ASSAYCLASS_URL}/assayclasses/C200010?application_context=HUBMAP" \
 --header "Accept: application/json"
echo

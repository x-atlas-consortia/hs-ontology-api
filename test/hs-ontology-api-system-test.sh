#!/bin/bash
set -e
set -u

#########
# FULL SYSTEM TEST SCRIPT
# This script calls endpoints of the hs-ontology-api to validate the environment, including
# responses to large response payloads or timeouts.
# Use the unit test script to check endpoints in all scenarios, such as bad parameters.
# This script calls the superset of endpoints in both hs-ontology-api and ubkg-api.
##########


###########
# Help function
##########
Help()
{
   # Display Help
   echo ""
   echo "****************************************"
   echo "HELP: hs-ontology-api SYSTEM TEST SCRIPT"
   echo | tee
   echo "Syntax: ./hs-ontology-api-system-test.sh [-option]..."
   echo "option" | tee
   echo "-v     test environment: l (local), d (DEV), or p (PROD)"
   echo "NOTE: This script writes output to a file named hs-ontology-system-$testout."
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


UBKG_URL_PROD=https://ontology.api.hubmapconsortium.org
UBKG_URL_DEV=https://ontology-api.dev.hubmapconsortium.org
UBKG_URL_TEST=https://ontology-api.test.hubmapconsortium.org
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
testout=hs-ontology-api-system-test.out

# UBKG_URL=$UBKG_URL_LOCAL
echo "Using UBKG instance at: ${UBKG_URL}" | tee $testout
echo "Only the first 60 characters of output from HTTP 200 returns displayed."

#--------------------------------------------
echo "ubkg-api endpoints"
echo

echo "/codes/SNOMEDCT_US%3A254837009/codes?sab=CHV,DOID"| tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/codes/SNOMEDCT_US%3A254837009/codes?sab=CHV,DOID" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/codes/SNOMEDCT_US%3A254837009/concepts" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/codes/SNOMEDCT_US%3A254837009/concepts" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/codes/SNOMEDCT_US%3A254837009/terms?term_type=PT" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/codes/SNOMEDCT_US%3A254837009/terms?term_type=PT" \
 --header "Accept: application/json" | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/C0678222/codes" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/C0678222/codes" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/C0010346/concepts" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/C4722518/concepts" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/C0678222/definitions" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/C0678222/definitions" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/paths/subgraph?sab=SNOMEDCT_US&rel=isa&skip=0&limit=10" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/paths/subgraph?sab=SNOMEDCT_US&rel=isa&skip=0&limit=10" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/C0006142/paths/subgraph/sequential?relsequence=NCI%3Ais_marked_by_gene_product,NCI%3Agene_product_encoded_by_gene&skip=0&limit=5" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/C0006142/paths/subgraph/sequential?relsequence=NCI:is_marked_by_gene_product,NCI:gene_product_encoded_by_gene&skip=0&limit=5" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/arm/nodeobjects" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/arm/nodeobjects" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/C2720507/paths/expand?sab=SNOMEDCT_US&rel=isa&mindepth=2&maxdepth=3&skip=0&limit=10" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/C2720507/paths/expand?sab=SNOMEDCT_US&rel=isa&mindepth=2&maxdepth=3&limit=10" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/C2720507/paths/trees?sab=SNOMEDCT_US&rel=isa&mindepth=1&maxdepth=3&skip=1&limit=10" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/C2720507/paths/trees?sab=SNOMEDCT_US&rel=isa&mindepth=1&maxdepth=3&skip=1&limit=10" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/concepts/C2720507/paths/shortestpath/C1272753?sab=SNOMEDCT_US&rel=isa" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/concepts/C2720507/paths/shortestpath/C1272753?sab=SNOMEDCT_US&rel=isa" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/node-types GET" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/node-types" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/node-types/Code/counts GET" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/node-types/Code/counts" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/node-types/Code/counts-by-sab?sab=SNOMEDCT_US GET " | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/node-types/Code/counts-by-sab?sab=SNOMEDCT_US" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/property-types GET" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/property-types" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/relationship-types GET" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/relationship-types" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/sabs GET" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/sabs" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/sabs/codes/counts?skip=5&limit=10" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/sabs/codes/counts?skip=5&limit=10" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/sabs/SNOMEDCT_US/codes/counts?skip=0&limit=10" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/sabs/SNOMEDCT_US/codes/counts?skip=0&limit=10" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/sabs/SNOMEDCT_US/codes/details?skip=0&limit=10" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/sabs/SNOMEDCT_US/codes/details?skip=0&limit=10" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/sabs/SNOMEDCT_US/term-types" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/sabs/SNOMEDCT_US/term-types" \
 --header "Accept: application/json"  | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/semantics/semantic-types" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/semantics/semantic-types?skip=1&limit=10" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "semantics/semantic-types/Anatomical%20Structure?&skip=0&limit=10" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/semantics/semantic-types/Anatomical%20Structure?&skip=0&limit=10" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo | tee -a $testout
echo "/semantics/semantic-types/Anatomical%20Structure/subtypes?skip=1&limit=10" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/semantics/semantic-types/Anatomical%20Structure/subtypes?skip=1&limit=10" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout

echo "/terms/codes/Breast%20cancer GET" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/terms/Breast%20cancer/codes" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

echo "/terms/Breast%20cancer/concepts GET" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/terms/Breast%20cancer/concepts" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout

echo "/sources?sab=HPOMP GET" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/sources?sab=HPOMP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo | tee -a $testout
echo | tee -a $testout

#--------------------------------------------
echo "hs-ontology-api endpoints"
echo

echo "/pathways/R-HSA-8953897/participants" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/R-HSA-8953897/participants" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/pathways/with-genes" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/pathways/with-genes" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/assayclasses" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/assayclasses?application_context=HUBMAP" \
--header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/dataset-types?application_context=HUBMAP" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/dataset-types?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo

echo "/organs?application_context=HUBMAP" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/organs/by-code?application_context=HUBMAP" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Accept: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "relationships/gene/MMRN1" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/relationships/gene/MMRN1" \
 --header "Content-Type: application/json"| cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/valueset?parent_sab=HUBMAP&parent_code=C003041&child_sabs=HUBMAP" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=HUBMAP&parent_code=C003041&child_sabs=HUBMAP" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/genes-info?page=1&genes_per_page=3" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=1&genes_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/genes/MMRN1" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/genes/MMRN1" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/proteins-info?page=1&proteins_per_page=3" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=1&proteins_per_page=3" \
 --header "Content-Type: application/json"| cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/proteins/MMRN1_HUMAN" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/proteins/MMRN1_HUMAN" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/celltypes-info?page=1&celltypes_per_page=3" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=1&celltypes_per_page=3" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/celltypes/2138,236" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/celltypes/2138,236" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/celltypes/0002138" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/celltypes/0002138" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/field-descriptions" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-descriptions" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/field-types" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/field-types-info" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-types-info" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/field-assays => should return 200" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-assays" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/field-entities" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-entities" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/field-schemas" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/field-schemas" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout

echo "/annotations?sab=AZ" | tee -a $testout
curl --request GET \
 --url "${UBKG_URL}/annotations?sab=AZ" \
 --header "Content-Type: application/json" | cut -c1-60 | tee -a $testout
echo
echo | tee -a $testout
echo | tee -a $testout
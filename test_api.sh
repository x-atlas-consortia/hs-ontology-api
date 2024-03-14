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
   echo "HELP: hs-ontology-api API test script"
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
 --header "Accept: application/json" |cut -c1-60
echo


echo "assaytype/<name> GET"
curl --request GET \
 --url "${UBKG_URL}/assaytype/bulk-RNA?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "datasets GET"
curl --request GET \
 --url "${UBKG_URL}/datasets?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "organs GET for HUBMAP"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "organs GET for SENNET"
curl --request GET \
 --url "${UBKG_URL}/organs?application_context=SENNET" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "organs/by-code GET"
curl --request GET \
 --url "${UBKG_URL}/organs/by-code?application_context=HUBMAP" \
 --header "Accept: application/json" |cut -c1-60
echo

echo "relationships/gene GET..."
curl --request GET \
 --url "${UBKG_URL}/relationships/gene/MMRN1" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "valueset GET..."
curl --request GET \
 --url "${UBKG_URL}/valueset?child_sabs=OBI&parent_sab=HUBMAP&parent_code=C001000" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Test for gene_list endpoint
echo "genes-info GET"
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=1&genes_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "genes-info GET last page"
curl --request GET \
 --url "${UBKG_URL}/genes-info?page=last&genes_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "genes-info GET starts_with B"
curl --request GET \
 --url "${UBKG_URL}/genes-info?genes_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Test for genes endpoint.
echo "genes GET for MMRN1"
curl --request GET \
 --url "${UBKG_URL}/genes/MMRN1" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Test for proteins-info endpoint.
echo "proteins-info GET"
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=1&proteins_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "proteins-info GET last page"
curl --request GET \
 --url "${UBKG_URL}/proteins-info?page=last&proteins_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "proteins-info GET starts_with B"
curl --request GET \
 --url "${UBKG_URL}/proteins-info?proteins_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" |cut -c1-60
echo
# Test for proteins endpoint.
echo "proteins GET for MMRN1_HUMAN"
curl --request GET \
 --url "${UBKG_URL}/proteins/MMRN1_HUMAN" \
 --header "Content-Type: application/json" |cut -c1-60
echo

# Test for celltypes list.
echo "celltypes-info GET"
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=1&celltypes_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "celltypes-info GET last page"
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?page=last&celltypes_per_page=3" \
 --header "Content-Type: application/json" |cut -c1-60
echo
echo "celltypes-info GET starts_with B"
curl --request GET \
 --url "${UBKG_URL}/celltypes-info?celltypes_per_page=3&starts_with=B" \
 --header "Content-Type: application/json" |cut -c1-60
echo
# Test for proteins endpoint.
echo "celltypes GET for 0002138"
curl --request GET \
 --url "${UBKG_URL}/celltypes/0002138" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "SENNET source types"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C020076&child_sabs=SENNET" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "SENNET sample categories"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C050020&child_sabs=SENNET" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "SENNET entities"
curl --request GET \
 --url "${UBKG_URL}/valueset?parent_sab=SENNET&parent_code=C000012&child_sabs=SENNET" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-descriptions"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-descriptions/acquisition_instrument_model"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-descriptions/acquisition_instrument_model?test=X"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?test=X" \
 --header "Content-Type: application/json"
echo

echo "field-descriptions/acquisition_instrument_model?source=X"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?source=X" \
 --header "Content-Type: application/json"
echo

echo "field-descriptions/acquisition_instrument_model?source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-descriptions/acquisition_instrument_model?source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types/acquisition_instrument_model"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types/acquisition_instrument_model?test=x"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?test=x" \
 --header "Content-Type: application/json"
echo

echo "field-types/acquisition_instrument_model?mapping_source=X"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?mapping_source=X" \
 --header "Content-Type: application/json"
echo

echo "field-types/acquisition_instrument_model?mapping_source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?mapping_source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types/acquisition_instrument_model?type_source=X"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type_source=X" \
 --header "Content-Type: application/json"
echo

echo "field-types/acquisition_instrument_model?type_source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type_source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types/acquisition_instrument_model?type=X"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type=X" \
 --header "Content-Type: application/json"
echo

echo "field-types/acquisition_instrument_model?type=string"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types/acquisition_instrument_model?type=string" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types-info"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types-info" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-types-info?test=x"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-types-info?test=x" \
 --header "Content-Type: application/json"
echo

echo "field-types-info?type_source=x"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-types-info?type_source=x" \
 --header "Content-Type: application/json"
echo

echo "field-types-info?type_source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-types-info?type_source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model?test=X"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-assays?test=X" \
 --header "Content-Type: application/json"
echo

echo "field-assays?assay_identifier=X"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-assays?assay_identifier=X" \
 --header "Content-Type: application/json"
echo

echo "field-assays?assay_identifier=snRNAseq"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays?assay_identifier=snRNAseq" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model?assay_identifier=snRNAseq"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model?assay_identifier=snRNAseq" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays?data_type=X"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-assays?data_type=X" \
 --header "Content-Type: application/json"
echo

echo "field-assays?data_type=seqFISH"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays?data_type=seqFISH" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model?data_type=seqFISH"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model?data_type=seqFISH" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays?dataset_type=X"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-assays?dataset_type=x" \
 --header "Content-Type: application/json"
echo

echo "field-assays?dataset_type=RNAseq"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays?dataset_type=RNAseq" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-assays/acquisition_instrument_model?dataset_type=RNAseq"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-assays/acquisition_instrument_model?dataset_type=RNAseq" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities?test=X"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-entities?test=X" \
 --header "Content-Type: application/json"
echo

echo "field-entities/umi_offset"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities/umi_offset?source=x"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset?source=x" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities/umi_offset?source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset?source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-entities/umi_offset?entity=x"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset?entity=x" \
 --header "Content-Type: application/json"
echo

echo "field-entities/umi_offset?entity=dataset"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-entities/umi_offset?entity=dataset" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-schemas"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-schemas?test=x"
echo "SHOULD RETURN 400; invalid parameter"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?test=x" \
 --header "Content-Type: application/json"
echo

echo "field-schemas/acquisition_instrument_model"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas/acquisition_instrument_model" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-schemas/acquisition_instrument_model?source=x"
echo "SHOULD RETURN 400; invalid parameter value"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?source=x" \
 --header "Content-Type: application/json"
echo

echo "field-schemas/acquisition_instrument_model?source=HMFIELD"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?source=HMFIELD" \
 --header "Content-Type: application/json" |cut -c1-60
echo

echo "field-schemas/acquisition_instrument_model?schema=x"
echo "SHOULD RETURN 404; no results"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?schema=x" \
 --header "Content-Type: application/json"
echo

echo "field-schemas/acquisition_instrument_model?schema=imc3d"
echo "SHOULD RETURN 200"
curl --request GET \
 --url "${UBKG_URL}/field-schemas?schema=imc3d" \
 --header "Content-Type: application/json" |cut -c1-60
echo
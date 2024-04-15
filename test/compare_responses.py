#!/usr/bin/env python3

import argparse
import requests
import json
from datatest import validate, ValidationError
# https://zepworks.com/deepdiff/6.7.1/
from deepdiff import DeepDiff
import pprint


UBKG_URL_PROD = 'https://ontology.api.hubmapconsortium.org'
UBKG_URL_DEV = 'https://ontology-api.dev.hubmapconsortium.org'
UBKG_URL_TEST = 'https://ontology-api.test.hubmapconsortium.org'

URL_LOCAL = 'http://127.0.0.1:5002'

DIFFERENCES_STATUS_CODE = 0
DIFFERENCES_RESPONSE = 0
ENDPOINTS_PROCESSED = 0
STATUS_CODE_500_HOST_A = 0
STATUS_CODE_500_HOST_B = 0


class RawTextArgumentDefaultsHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawTextHelpFormatter
):
    pass


# https://docs.python.org/3/howto/argparse.html
parser = argparse.ArgumentParser(
    description="""
    Check for differences between endpoints from two UBKG micro-services.
    
    For example executing:
    % src/compare_responses.py https://ontology.api.hubmapconsortium.org http://127.0.0.1:5002 -d
    Will compare the results from microservice on ontology.api.hubmapconsortium.org to the
    one running on localhost using deepdiff to do the comparison of the output.
    
    Without using one of '-t', '-d', or '-V' only endpoint status differences will be flagged.
    
    For documentation on DeepDiff see: https://zepworks.com/deepdiff/6.7.1/diff.html
    """,
    formatter_class=RawTextArgumentDefaultsHelpFormatter)
parser.add_argument('host_a', type=str, default=UBKG_URL_PROD,
                    help='host to be compared too (expected)')
parser.add_argument('host_b', type=str, default=URL_LOCAL,
                    help='host to check for differences')
parser.add_argument("-t", "--textual", action="store_true",
                    help='show textual differences')
parser.add_argument("-d", "--deepdiff", action="store_true",
                    help='show differences using DeepDiff')
parser.add_argument("-V", "--validate", action="store_true",
                    help='show differences using Validate')
parser.add_argument("-v", "--verbose", action="store_true",
                    help='increase output verbosity')

args = parser.parse_args()


def endpoint_get_diff(host_a: str, host_b: str, path) -> None:
    resp_a = requests.get(f"{host_a}{path}")
    resp_b = requests.get(f"{host_b}{path}")
    resp_diff(host_a, host_b, path, resp_a, resp_b)


def endpoint_post_diff(host_a: str, host_b: str, path: str, data: dict) -> None:
    resp_a = requests.post(f"{host_a}{path}", json=data)
    resp_b = requests.post(f"{host_b}{path}", json=data)
    resp_diff(host_a, host_b, path, resp_a, resp_b)


def resp_diff(host_a: str, host_b: str, path: str, resp_a, resp_b) -> None:
    global DIFFERENCES_STATUS_CODE, DIFFERENCES_RESPONSE, ENDPOINTS_PROCESSED
    global STATUS_CODE_500_HOST_A, STATUS_CODE_500_HOST_B
    print(f"Checking path: {path} ", end='')
    ENDPOINTS_PROCESSED += 1
    if resp_a.status_code == 500:
        STATUS_CODE_500_HOST_A += 1
    if resp_b.status_code == 500:
        STATUS_CODE_500_HOST_B += 1
    if resp_a.status_code != resp_b.status_code:
        print(f"\nSTATUS CODES DIFFER: {host_a}:{resp_a.status_code}; {host_b}:{resp_b.status_code}")
        DIFFERENCES_STATUS_CODE += 1
        return
    if resp_a.text != resp_b.text:
        DIFFERENCES_RESPONSE += 1
        if args.textual is True:
            print(f"\nDIFFERENCES (Textual): {host_a}:{resp_a.text}; {host_b}:{resp_b.text}")
        resp_a_dict: dict = json.loads(resp_a.text)
        resp_b_dict: dict = json.loads(resp_b.text)
        if args.deepdiff is True:
            # https://zepworks.com/deepdiff/6.7.1/diff.html
            deepdiff = DeepDiff(resp_b_dict, resp_a_dict,
                                ignore_order=True, ignore_string_case=True,
                                report_repetition=True, verbose_level=2
                                )
            print('DIFFERENCE (DeepDiff):')
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(deepdiff)
        if args.validate is True:
            try:
                validate(resp_b_dict, resp_a_dict)
            except ValidationError as ve:
                # https://datatest.readthedocs.io/en/stable/reference/datatest-core.html#datatest.ValidationError
                print('DIFFERENCES (Validate):')
                print(f"Expected (host_a): {ve.differences[0].expected}")
                print(f"Found (host_b): {ve.differences[0].invalid}")
                print()

        return
    print('OK!')


def diff(host_a: str, host_b: str) -> None:
    endpoint_post_diff(host_a, host_b, '/assayname', {"name": "bulk-RNA"})
    endpoint_get_diff(host_a, host_b, '/assaytype?application_context=HUBMAP')
    endpoint_get_diff(host_a, host_b, '/assaytype/bulk-RNA?application_context=HUBMAP')
    endpoint_get_diff(host_a, host_b, '/datasets?application_context=HUBMAP')
    endpoint_get_diff(host_a, host_b, '/organs?application_context=HUBMAP')
    endpoint_get_diff(host_a, host_b, '/organs?application_context=SENNET')
    endpoint_get_diff(host_a, host_b, '/organs/by-code?application_context=HUBMAP')
    endpoint_get_diff(host_a, host_b, '/relationships/gene/MMRN1')
    endpoint_get_diff(host_a, host_b, '/valueset?child_sabs=OBI&parent_sab=HUBMAP&parent_code=C001000')
    endpoint_get_diff(host_a, host_b, '/genes-info?page=1&genes_per_page=3')
    endpoint_get_diff(host_a, host_b, '/genes-info?page=last&genes_per_page=3')
    endpoint_get_diff(host_a, host_b, '/genes-info?genes_per_page=3&starts_with=B')
    endpoint_get_diff(host_a, host_b, '/genes/MMRN1')
    endpoint_get_diff(host_a, host_b, '/proteins-info?page=1&proteins_per_page=3')
    endpoint_get_diff(host_a, host_b, '/proteins-info?page=last&proteins_per_page=3')
    endpoint_get_diff(host_a, host_b, '/proteins-info?proteins_per_page=3&starts_with=B')
    endpoint_get_diff(host_a, host_b, '/proteins/MMRN1_HUMAN')
    endpoint_get_diff(host_a, host_b, '/celltypes-info?page=1&proteins_per_page=3')
    endpoint_get_diff(host_a, host_b, '/celltypes-info?page=last&proteins_per_page=3')
    endpoint_get_diff(host_a, host_b, '/celltypes-info?proteins_per_page=3&starts_with=B')
    endpoint_get_diff(host_a, host_b, '/celltypes/0002138')
    endpoint_get_diff(host_a, host_b, '/valueset?parent_sab=SENNET&parent_code=C020076&child_sabs=SENNET')
    endpoint_get_diff(host_a, host_b, '/valueset?parent_sab=SENNET&parent_code=C050020&child_sabs=SENNET')
    endpoint_get_diff(host_a, host_b, '/valueset?parent_sab=SENNET&parent_code=C000012&child_sabs=SENNET')
    endpoint_get_diff(host_a, host_b, '/field-descriptions')
    endpoint_get_diff(host_a, host_b, '/field-descriptions/acquisition_instrument_model')
    endpoint_get_diff(host_a, host_b, '/field-descriptions/acquisition_instrument_model?test=X')
    endpoint_get_diff(host_a, host_b, '/field-descriptions/acquisition_instrument_model?source=X')
    endpoint_get_diff(host_a, host_b, '/field-descriptions/acquisition_instrument_model?source=HMFIELD')
    endpoint_get_diff(host_a, host_b, '/field-types')
    endpoint_get_diff(host_a, host_b, '/field-types/acquisition_instrument_model')
    endpoint_get_diff(host_a, host_b, '/field-types/acquisition_instrument_model?test=x')
    endpoint_get_diff(host_a, host_b, '/field-types/acquisition_instrument_model?mapping_source=X')
    endpoint_get_diff(host_a, host_b, '/field-types/acquisition_instrument_model?mapping_source=HMFIELD')
    endpoint_get_diff(host_a, host_b, '/field-types/acquisition_instrument_model?type_source=X')
    endpoint_get_diff(host_a, host_b, '/field-types/acquisition_instrument_model?type_source=HMFIELD')
    endpoint_get_diff(host_a, host_b, '/field-types/acquisition_instrument_model?type=X')
    endpoint_get_diff(host_a, host_b, '/field-types/acquisition_instrument_model?type=string')
    endpoint_get_diff(host_a, host_b, '/field-types-info')
    endpoint_get_diff(host_a, host_b, '/field-types-info?test=x')
    endpoint_get_diff(host_a, host_b, '/field-types-info?type_source=x')
    endpoint_get_diff(host_a, host_b, '/field-types-info?type_source=HMFIELD')
    endpoint_get_diff(host_a, host_b, '/field-assays')
    endpoint_get_diff(host_a, host_b, '/field-assays/acquisition_instrument_model')
    endpoint_get_diff(host_a, host_b, '/field-assays?test=X')
    endpoint_get_diff(host_a, host_b, '/field-assays?assay_identifier=X')
    endpoint_get_diff(host_a, host_b, '/field-assays?assay_identifier=snRNAseq')
    endpoint_get_diff(host_a, host_b, '/field-assays/acquisition_instrument_model?assay_identifier=snRNAseq')
    endpoint_get_diff(host_a, host_b, '/field-assays?data_type=X')
    endpoint_get_diff(host_a, host_b, '/field-assays?data_type=seqFISH')
    endpoint_get_diff(host_a, host_b, '/field-assays/acquisition_instrument_model?data_type=seqFISH')
    endpoint_get_diff(host_a, host_b, '/field-assays?dataset_type=x')
    endpoint_get_diff(host_a, host_b, '/field-assays?dataset_type=RNAseq')
    endpoint_get_diff(host_a, host_b, '/field-assays/acquisition_instrument_model?dataset_type=RNAseq')
    endpoint_get_diff(host_a, host_b, '/field-entities')
    endpoint_get_diff(host_a, host_b, '/field-entities?test=X')
    endpoint_get_diff(host_a, host_b, '/field-entities/acquisition_instrument_model')
    endpoint_get_diff(host_a, host_b, '/field-entities/acquisition_instrument_model?source=x')
    endpoint_get_diff(host_a, host_b, '/field-entities/acquisition_instrument_model?source=HMFIELD')
    endpoint_get_diff(host_a, host_b, '/field-entities/acquisition_instrument_model?entity=x')
    endpoint_get_diff(host_a, host_b, '/field-entities/acquisition_instrument_model?entity=dataset')
    endpoint_get_diff(host_a, host_b, '/field-schemas')
    endpoint_get_diff(host_a, host_b, '/field-schemas?test=x')
    endpoint_get_diff(host_a, host_b, '/field-schemas/acquisition_instrument_model')
    endpoint_get_diff(host_a, host_b, '/field-schemas?source=x')
    endpoint_get_diff(host_a, host_b, '/field-schemas?source=HMFIELD')
    endpoint_get_diff(host_a, host_b, '/field-schemas?schema=x')
    endpoint_get_diff(host_a, host_b, '/field-schemas?schema=imc3d')


diff(args.host_a, args.host_b)
print(f"\nEndpoints processed: {ENDPOINTS_PROCESSED}; "
      f"Response Differences: {DIFFERENCES_RESPONSE}"
      f"\nStatus Code Differences: {DIFFERENCES_STATUS_CODE}; "
      f"Status Codes 500 {args.host_a}: {STATUS_CODE_500_HOST_A}; "
      f"Status Codes 500 {args.host_b}: {STATUS_CODE_500_HOST_B} "
      )
print("\nDone!")

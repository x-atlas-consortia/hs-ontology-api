import os
import json
from flask import Flask, request, Response, abort
from urllib.request import urlopen
from urllib.error import HTTPError
import logging

#
# This is a RESTful service that exposes two endpoints:
#     /assayclasses?application_context=HUBMAP
#     /assayclasses/<assay-code>?application_context=HUBMAP
#
# Both endpoints require the application_context=HUBMAP parameter to be included, otherwise they return a 400.
#
# This service is intended to be for development purposes only, so a developer can easily control the output by
# changing the [assayclasses.json file in GitHub], specified in the ASSAYCLASSES_JSON_URL app.conf parameter.
#
# It is intended to mimic the services:
#     https://ontology-api.dev.hubmapconsortium.org/assayclasses?application_context=HUBMAP
#     https://ontology-api.dev.hubmapconsortium.org/assayclasses/C200150?application_context=HUBMAP
#
# Please see Issue: https://github.com/orgs/hubmapconsortium/projects/40/views/1?filterQuery=kollar&visibleFields=%5B%22Title%22%2C%22Assignees%22%2C%22Status%22%2C%22Labels%22%2C117184707%5D&pane=issue&itemId=74945308


logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )
logger = logging.getLogger()


app = Flask(__name__,
            instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'),
            instance_relative_config=True)
app.config.from_pyfile('app.cfg')


def get_assayclasses() -> dict:
    """
    Download the assayclasses information and return it as a dict.
    Since this is done at startup time, on error it will log an error and exit as the app cannot recover from this.
    """
    if "ASSAYCLASSES_JSON_URL" not in app.config:
        logger.error("app.cfg must contain ASSAYCLASSES_JSON_URL")
        exit(1)
    assayclasses_json_url: str = app.config["ASSAYCLASSES_JSON_URL"]
    try:
        response = urlopen(assayclasses_json_url)
        data: str = response.read().decode("utf-8")
    except HTTPError as he:
        logger.error(f"Could not read ASSAYCLASSES_JSON_URL: {assayclasses_json_url}, error: {he}")
        exit(1)
    try:
        json_dict: dict = json.loads(data)
    except json.JSONDecodeError as jde:
        logger.error(f"Invalid JSON syntax: {jde}")
        exit(1)
    logger.info(f"successfully downloaded app.cfg:ASSAYCLASSES_JSON_URL={assayclasses_json_url} json as dict")
    return json_dict


assayclasses_list: dict = get_assayclasses()


def find_assayclass_with_rule_description_code(code: str):
    """
    Find the assayclass corresponding the rule_description code given or return None.
    """
    for ad in assayclasses_list:
        if "rule_description" in ad and "code" in ad["rule_description"] and ad["rule_description"]["code"] == code:
            return ad
    return None


def check_for_valid_application_context() -> None:
    """
    Check for a valid auery parameter application_context, and if not found abort with a 400.
    """
    application_context = request.args.get('application_context')
    if application_context is None or application_context.upper() != "HUBMAP":
        abort(Response(json.dumps({"message": "A query parameter of application_context=HUBMAP must be specified"}),
                       400,
                       mimetype='application/json'))


@app.route('/', methods=['GET'])
def index():
    return "Hello! This is the DEV AssayClass service :)"


@app.route('/assayclasses/<code>', methods=['GET'])
def assayclasses_by_code(code):
    """
    This endpoint searches the same assayclasses.json file for an assayclass item matching
    rule_description.code and returns the full matching assayclass item as a json response.
    If the code is not found a 404 is returned.
    """
    check_for_valid_application_context()

    assayclass_dict = find_assayclass_with_rule_description_code(code)

    if assayclass_dict is not None:
        return Response(json.dumps(assayclass_dict), 200, mimetype='application/json')

    return Response(json.dumps({"message": f"No assayclass corresponding the rule_description code:{code} was found"}),
                    404, mimetype='application/json')


@app.route('/assayclasses', methods=['GET'])
def assayclass():
    """
    This endpoint returns the contents of the ASSAYCLASSES_JSON_URL as a json response.
    """
    check_for_valid_application_context()

    return Response(json.dumps(assayclasses_list), 200, mimetype='application/json')


# For development/testing only
if __name__ == '__main__':
    try:
        port = 8181
        app.run(port=port, host='0.0.0.0')
    finally:
        pass

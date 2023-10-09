# coding: utf-8
# JAS October 2023
from flask import Blueprint, jsonify, current_app, request
from ..neo4j_logic import genesfromcells_get_logic
from ..cellsclient import OntologyCellsClient

geneslist_blueprint = Blueprint('geneslist', __name__, url_prefix='/geneslist')

# Ontology Cells Client - wrapper around Cells API Python client (hubmap-api-py-client)
ontcells = OntologyCellsClient()

@geneslist_blueprint.route('', methods=['GET'])
def geneslist() -> list[str]:

    neo4j_instance = current_app.neo4jConnectionHelper.instance()

    # Obtain a list of genes that the Cells API identifies as being in datasets.
    return jsonify(ontcells.genes_from_cells())
# coding: utf-8
# JAS October 2023
from flask import Blueprint, jsonify, current_app, request
from ..neo4j_logic import genesfromcells_get_logic
from ..cellsclient import OntologyCellsClient

genesfromcells_blueprint = Blueprint('genesfromcells', __name__, url_prefix='/genesfromcells')

# Ontology Cells Client - wrapper around Cells API Python client (hubmap-api-py-client)
ontcells = OntologyCellsClient()

@genesfromcells_blueprint.route('', methods=['GET'])
def genesfromcells() -> list[str]:

    neo4j_instance = current_app.neo4jConnectionHelper.instance()

    # Obtain a list of genes that the Cells API identifies as being in datasets.
    return jsonify(ontcells.genes_from_cells())
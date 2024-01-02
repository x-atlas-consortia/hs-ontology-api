from os import path
from flask import Flask, jsonify, current_app
from pathlib import Path
from ubkg_api.app import UbkgAPI, logger

from hs_ontology_api.routes.assaytype.assaytype_controller import assaytype_blueprint
from hs_ontology_api.routes.assayname.assayname_controller import assayname_blueprint
from hs_ontology_api.routes.datasets.datasets_controller import datasets_blueprint
from hs_ontology_api.routes.organs.organs_controller import organs_blueprint
from hs_ontology_api.routes.relationships.relationships_controller import relationships_blueprint
from hs_ontology_api.routes.valueset.valueset_controller import valueset_blueprint
# JAS September 2023
from hs_ontology_api.routes.genes.genes_controller import genes_blueprint
from hs_ontology_api.routes.genesinfo.genesinfo_controller import genesinfo_blueprint
# JAS November 2023
from hs_ontology_api.routes.proteins.proteins_controller import proteins_blueprint
from hs_ontology_api.routes.proteinsinfo.proteinsinfo_controller import proteinsinfo_blueprint
from hs_ontology_api.routes.celltypes.celltypes_controller import celltypes_blueprint
from hs_ontology_api.routes.celltypesinfo.celltypesinfo_controller import celltypesinfo_blueprint
# JAS December 2023
from hs_ontology_api.routes.fielddescriptions.fielddescriptions_controller import field_descriptions_blueprint
from hs_ontology_api.routes.fieldtypes.fieldtypes_controller import field_types_blueprint
from hs_ontology_api.routes.fieldassays.fieldassays_controller import field_assays_blueprint
# JAS January 2024
from hs_ontology_api.routes.fieldschemas.fieldschemas_controller import field_schemas_blueprint
from hs_ontology_api.routes.fieldtypesinfo.fieldtypesinfo_controller import field_types_info_blueprint

# Cells API client
from hs_ontology_api.utils.cellsclient import OntologyCellsClient


def make_flask_config():
    temp_flask_app = Flask(__name__,
                      instance_path=path.join(path.abspath(path.dirname(__file__)), 'hs_ontology_api/instance'),
                      instance_relative_config=True)
    temp_flask_app.config.from_pyfile('app.cfg')
    return temp_flask_app.config


app = UbkgAPI(make_flask_config()).app
app.register_blueprint(assaytype_blueprint)
app.register_blueprint(assayname_blueprint)
app.register_blueprint(datasets_blueprint)
app.register_blueprint(organs_blueprint)
app.register_blueprint(relationships_blueprint)
app.register_blueprint(valueset_blueprint)
# JAS Sept 2023
app.register_blueprint(genes_blueprint)
app.register_blueprint(genesinfo_blueprint)
# JAS Nov 2023
app.register_blueprint(proteins_blueprint)
app.register_blueprint(proteinsinfo_blueprint)
app.register_blueprint(celltypesinfo_blueprint)
app.register_blueprint(celltypes_blueprint)
# JAS Dec 2023
app.register_blueprint(field_descriptions_blueprint)
app.register_blueprint(field_types_blueprint)
app.register_blueprint(field_assays_blueprint)
# JAS Jan 2024
app.register_blueprint(field_schemas_blueprint)
app.register_blueprint(field_types_info_blueprint)


# Instantiate a Cells API client.
cellsurl = make_flask_config().get('CELLSURL')
app.cells_client = OntologyCellsClient(cellsurl)


# Defining the /status endpoint in the ubkg_api package will cause 500 error
# Because the VERSION and BUILD files are not built into the package
@app.route('/status', methods=['GET'])
def api_status():
    status_data = {
        # Use strip() to remove leading and trailing spaces, newlines, and tabs
        'version': (Path(__file__).absolute().parent.parent / 'VERSION').read_text().strip(),
        'build': (Path(__file__).absolute().parent.parent / 'BUILD').read_text().strip(),
        'neo4j_connection': False
    }
    is_connected = current_app.neo4jConnectionHelper.check_connection()
    if is_connected:
        status_data['neo4j_connection'] = True

    return jsonify(status_data)

####################################################################################################
## For local development/testing
####################################################################################################

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port="5002")
    except Exception as e:
        print("Error during starting debug server.")
        print(str(e))
        logger.error(e, exc_info=True)
        print("Error during startup check the log file for further information")

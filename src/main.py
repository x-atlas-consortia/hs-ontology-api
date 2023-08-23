from os import path
from flask import Flask, jsonify, current_app
from pathlib import Path
from ubkg_api.app import UbkgAPI, logger

from hs_ontology_api.routes.datasets.datasets_controller import datasets_blueprint
from hs_ontology_api.routes.organs.organs_controller import organs_blueprint
from hs_ontology_api.routes.relationships.relationships_controller import relationships_blueprint
from hs_ontology_api.routes.valueset.valueset_controller import valueset_blueprint


def make_flask_config():
    temp_flask_app = Flask(__name__,
                      instance_path=path.join(path.abspath(path.dirname(__file__)), 'hs_ontology_api/instance'),
                      instance_relative_config=True)
    temp_flask_app.config.from_pyfile('app.cfg')
    return temp_flask_app.config


app = UbkgAPI(make_flask_config()).app
app.register_blueprint(datasets_blueprint)
app.register_blueprint(organs_blueprint)
app.register_blueprint(relationships_blueprint)
app.register_blueprint(valueset_blueprint)


# Define the /status endpoint in the ubkg_api package will causes 500 error
# Because the VERSION and BUILD files are not built into the package
@app.route('/status', methods=['GET'])
def api_status():
    status_data = {
        # Use strip() to remove leading and trailing spaces, newlines, and tabs
        'version': (Path(__file__).absolute().parent.parent / 'VERSION').read_text().strip(),
        'build': (Path(__file__).absolute().parent.parent / 'BUILD').read_text().strip(),
        'neo4j_connection': False
    }
    is_connected = current_app.neo4jManager.check_connection()
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

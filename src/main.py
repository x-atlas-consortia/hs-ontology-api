import os
from flask import Flask, jsonify
from pathlib import Path
from ubkg_api.app import UbkgAPI, logger

from src.routes.valueset_controller import valueset_blueprint

flask_app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'), instance_relative_config=True)
flask_app.config.from_pyfile('app.cfg')

app = UbkgAPI(flask_app.config).app
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
    is_connected = app.neo4jManager.check_connection()
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
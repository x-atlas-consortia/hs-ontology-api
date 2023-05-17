import os
from flask import Flask
from ubkg_api.app import UbkgAPI

flask_app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'), instance_relative_config=True)
flask_app.config.from_pyfile('app.cfg')

app = UbkgAPI(flask_app.config).app


# For local standalone (non-docker) development/testing
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port="5002")
    except Exception as e:
        print("Error during starting debug server.")
        print(str(e))
        logger.error(e, exc_info=True)
        print("Error during startup check the log file for further information")
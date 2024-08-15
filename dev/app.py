import os
import json
from flask import Flask, Response

# Specify the absolute path of the instance folder and use the config file relative to the instance path
app = Flask(__name__,
            instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'),
            instance_relative_config=True)
app.config.from_pyfile('app.cfg')

@app.route('/', methods=['GET'])
def index():
    return "Hello! This is the DEV AssayClass service :)"

@app.route('/assayclasses/<code>', methods=['GET'])
def assayclasses(code):
    response_code = 200
    response_data = {
        'message': f'This endpoint not yet implemented code: {code}'
    }

    return Response(json.dumps(response_data), response_code, mimetype='application/json')

@app.route('/assayclasses', methods=['GET'])
def assayclass_by_code():
    response_code = 200
    response_data = {
        'message': 'This endpoint not yet implemented'
    }

    return Response(json.dumps(response_data), response_code, mimetype='application/json')


# For development/testing only
if __name__ == '__main__':
    try:
        port = 8181
        app.run(port=port, host='0.0.0.0')
    finally:
        pass

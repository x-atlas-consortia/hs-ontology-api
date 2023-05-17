from ubkg_api.app import app


# For local standalone (non-docker) development/testing
if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
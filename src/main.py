from ubkg_api.app import UbkgAPI


run_with_config_file = True

if __name__ == "__main__":
    if run_with_config_file:
        UbkgAPI(None).app.run(host='0.0.0.0', debug=True, port=8080)
    else:
        UbkgAPI({'SERVER': '', 'USERNAME': '', 'PASSWORD': ''}).app.run(host='0.0.0.0', debug=True, port=8080)


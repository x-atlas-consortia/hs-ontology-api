# Ontology API for HuBMAP and SenNet applications

Like [ubkg-api](https://github.com/x-atlas-consortia/ubkg-api), the hs-ontology-api is a Flask web application with 
Blueprint extensions that provides a REST API for parameterized queries against an 
instance of a [UBKG](https://ubkg.docs.xconsortia.org/) neo4j instance. 
The hs-ontology-api is specific to the [HuBMAP/SenNet context](https://ubkg.docs.xconsortia.org/contexts/#hubmapsennet-context) 
of UBKG: it manages endpoints that assume that the UBKG instance includes content ingested
from SABs related to HuBMAP and SenNet. The UBKG-api contains code that is 
common to all UBKG contexts.

By default, hs-ontology-api imports ubkg-api that has been compiled 
as a PyPi package. 

![img.png](img.png)

# Development/testing environment for hs-ontology-api

To enhance or fix an endpoint in the hs-ontology-api, you will need to
establish an application environment on the development machine. 
This includes:
1. An instance of a HuBMAP/SenNet UBKG context--i.e., an instance of neo4j populated with HubMAP/SenNet UBKG content. Options include:
   - a local bare-metal instance of neo4j
   - a local Docker install of a UBKG distribution built from [ubkg-neo4j](https://github.com/x-atlas-consortia/ubkg-neo4j) 
   - a cloud-based instance (development or production)
2. An instance of ubkg-api
3. An instance of hs-ontology-api
4. URLs that execute endpoints against the local instance of hs-ontology-api

## Connecting to a neo4j instance
To connect your branch of hs-ontology-api to a neo4j instance:
1. Copy the file file named **app.cfg.example** in the src/hs-ontology-api/instance folder to a file named **app.cfg**. 
2. Add to app.cfg the connection information for the neo4j instance.
The .gitignore file at the root of this repo will force git to exclude the app.cfg file from commits.

### Example neo4j connect string values for app.cfg
1. If you are working with a local Docker distribution installed via the **run.sh** script from [ubkg-neo4j](https://github.com/x-atlas-consortia/ubkg-neo4j), then
   - SERVER = 'bolt://localhost:b', where b is the port that you provided to run.sh with the **-b** flag
   - USERNAME = the value that you provided to run.sh with the **-u** flag
   - PASSWORD = the value that you provided to run.sh with the **-p** flag
2. The HuBMAP/SenNet cloud instances have the following values for SERVER:
   - Dev: https://ontology-api.dev.hubmapconsortium.org
   - Prod: https://ontology.api.hubmapconsortium.org

### Starting your neo4j instance
If you are using a local instance of the UBKG, the instance should be running. In particular, if you installed a local Docker instance of UBKG, be sure that Docker Desktop is running. If the neo4j instance is not available, calls to API endpoints will result in a 500 error.

## Connecting to a ubkg-api instance
If you are modifying code only in hs-ontology-api, you will only need
to use the PyPy package version of ubkg-api. The package is included in the requirements.txt file of this repo.

If you need to modify both the hs-ontology-api and ubkg-api in concert, you will
need to work with a local instance of the ubkg-api. This is possible by doing the following:
1. Check out a branch of ubkg-api.
2. Configure the local branch of ubkg-api, similarly to the local instance of hs-ontology-api.
3. Start the local instance of ubkg-api.
4. In the virtual environment for hs-ontology-api, install the local instance of ubkg-api using pip with the **-e** flag. This will override the pointer to the ubkg-api package. 

``pip install -e path/to/local/ubkg/repo``

## Connecting to the local instance of hs-ontology-api
For URLs that execute endpoints in your local instance, use the values indicated in the **main.py** script, in the section prefaced with the comment `For local development/testing`:

For example, if main.py indicates
``
app.run(host='0.0.0.0', port="5002")
``

then your test endpoint URLs should start with `http://127.0.0.1:5002/`

# Testing changes
To test changes to hs-ontology-api, you will need to start a local instance of your local API.

The following assumes that you have created a local branch of hs-ontology-api.

### From the command line
1. Move to the root of your local branch.
2. Create a Python virtual environment. The following command creates a virtual environment named _venv_.

   ``python -m venv venv``
3. Activate the virtual environment.
   
   ``source venv/bin/activate``
4. Move to the /src folder and install dependencies, inclduing the ubkg-api package.
   
   ``pip install -r requirements.txt``

5. Run main.py to start the local instance of the API.
   
   ``python main.py``


### In PyCharm
1. Create a new project based on a local clone of hs-ontology-api. PyCharm should establish a virtual environment.
2. Use the Python Packages tab to install the packages listed in **requirements.txt**.
3. In the Terminal window, run main.py.
4. Note that you may need to enable execute permissions on the main.py script before you can run it locally--e.g., with a command like ``chmod 777 main.py``

### URL testing

Once you have connected your instance of hs-ontology-api to instances of both neo4j and ubkg-api, run the following tests:
1. Paste the root endpoint URL into a browser window--e.g.,``http://127.0.0.1:5002/``. You should see a window with the status message `Hello! This is UBKG-API service :)`. The status message verifies that your local instance of hs-ontology-api is connected to an instance of ubkg-api.
2. Add to the root endpoint URL to execute a known endpoint--e.g., ``http://127.0.0.1:5002/datasets?application_context=HUBMAP``. You should see a response from either the hs-ontology-api or the ubkg-api, depending on the endpoint and your development configuration.
3. If you are only testing hs-ontology-api endpoints and using the PyPi install of ubkg-api, calls to endpoints managed by the ubkg-api will fail with a 500 error. To test endpoints from both hs-ontology-api and ubkg-api, you will need a local instance of ubkg-api that connects to the same instance of neo4j that the instance of hs-ontology-api connects to.

Various methods of testing endpoint URLs are possible, including:
1. **curl**, from either the command line or a shell script
2. Requests in Postman
3. A Python script using **Requests** or **pytest**
4. Executing directly in the browser. This method is suitable for GET endpoints.
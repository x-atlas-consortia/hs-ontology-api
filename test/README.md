# Ontology API for HuBMAP and SenNet applications

## Test scripts

### Background

#### UBKG API deployment 
The hs-ontology-api is a [child UBKG API](https://ubkg.docs.xconsortia.org/api/#child-ubkg-api-instances). 
The hs-ontology-api contains code for endpoints that work with a UBKG instance in the HuBMAP/SenNet [context](https://ubkg.docs.xconsortia.org/contexts/)--
i.e., with data specific to HuBMAP and SenNet; however, it also accepts calls to endpoints of the
generic UBKG base context. The code for generic endpoints is stored in the ubkg-api; 
the hs-ontology-api integrates with the ubkg-api that is compiled as a library 
(PyPi package).

A **UBKG API deployment** corresponds to the combination of the ubkg-api and one or more child APIs. 
The HuBMAP/SenNet UBKG API deployment combines ubkg-api and hs-ontology-api.

#### API Gateway
The endpoint URLs for the HuBMAP/SenNet UBKG API deployment are managed by a AWS API Gateway.
The gateway manages the union of all endpoint URLs.

### Types of Testing

#### Endpoints: unit and regression testing
To unit test or regression test endpoints of a UBKG API deployment, the developer should
work within the API instance that houses the endpoint code. In other words,
test hs-ontology-api endpoints by instantiating hs-ontology-api; test ubkg-api
endpoints by instantiating ubkg-api. 

In particular, testing new functionality in ubkg-api by executing against an instance
of hs-ontology-api is not a valid test methodology. Because the hs-ontology-api
works with a compiled package version of ubkg-api, it is better to test ubkg-api
endpoints in a development ubkg-api instance; once the ubkg-api endpoint is validated, the 
ubkg-api package can be recompiled for use by the hs-ontology-api.

To test hs-ontology-api endpoints, use the **test_api.s**h script in this folder. 
The script writes output to the test.out file, which is ignored by git.

#### Gateway: integration testing
Because the API gateway manages the endpoint URLs of all components of a UBKG API instance, it
is often necessary to test the union of endpoint URLs. This is not a functional test of a particular endpoint; 
instead, it is an integration test of the gateway configuration.

To test the gateway for the HuBMAP/SenNet UBKG API deployment, use the **test_gateway.sh** script in this folder.

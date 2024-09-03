## Development AssayClasses RESTful service

The service contained within this directory exposes two endpoints:
  - /assayclasses?application_context=HUBMAP
  - assayclasses/<assay-code>?application_context=HUBMAP

To run this service, in this directory:
  - copy instance/app.cfg.example to instance/app.cfg
  - create a python virtual environment with the contents of requirements.txt imported into the environment
  - source/activage the virtual environment
  - execute `python app.py`
The service will be available on port 8181.

Both endpoints require the `application_context=HUBMAP` parameter.  (A future version will allow SENNET context as well, which will read results from a different file).

The `/assayclasses` endpoint simply returns the contents of the file https://raw.githubusercontent.com/x-atlas-consortia/hs-ontology-api/dev-integrate/dev/assayclasses.json as a json response.

The `/assayclasses/<assay-code>` endpoint searches the same [assayclasses.json file](https://raw.githubusercontent.com/x-atlas-consortia/hs-ontology-api/dev-integrate/dev/assayclasses.json) for an assayclass item matching `rule_description.code` and returns the full matching assayclass item as a json response.  If the code is not found a 404 is returned.  For example if `/assayclasses/C200001?application_context=HUBMAP` is called the return value is:

```
{
  "rule_description": {
    "application_context": "HUBMAP",
    "code": "C200150",
    "name": "non-DCWG primary IMC2D"
  },
  "value": {
    "active_status": "active",
    "assaytype": "IMC2D",
    "dataset_type": {
      "PDR_category": "MxNF",
      "dataset_type": "2D Imaging Mass Cytometry",
      "fig2": {
        "aggregated_assaytype": "LC-MS",
        "category": "bulk",
        "modality": "Proteomics"
      }
    },
    "description": "2D Imaging Mass Cytometry",
    "dir_schema": "imc-v0",
    "is_multiassay": false,
    "measurement_assay": {
      "codes": [
        {
          "code": "SENNET:C006901",
          "term": "Imaging Mass Cytometry Measurement Assay"
        },
        {
          "code": "HUBMAP:C006901",
          "term": "Imaging Mass Cytometry Measurement Assay"
        },
        {
          "code": "OBI:0003096",
          "term": "imaging mass cytometry assay"
        }
      ],
      "contains_full_genetic_sequences": false
    },
    "must_contain": [],
    "pipeline_shorthand": null,
    "process_state": "primary",
    "provider": "IEC",
    "tbl_schema": "imc-v",
    "vitessce_hints": []
  }
}
```

## Deployment on DEV VM

First build a new docker image using the Dockerfile. Then spin up the container

```
docker run -it -d <image-name> -p 8181:8181 --restart=always
```
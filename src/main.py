from os import path
from flask import Flask
from pathlib import Path

# UBKG API package
from ubkg_api.app import UbkgAPI, logger

from hs_ontology_api.routes.organs.organs_controller import organs_blueprint
from hs_ontology_api.routes.relationships.relationships_controller import relationships_blueprint
from hs_ontology_api.routes.valueset.valueset_controller import valueset_blueprint
from hs_ontology_api.routes.genes.genes_controller import genes_blueprint
from hs_ontology_api.routes.genesinfo.genesinfo_controller import genesinfo_blueprint
from hs_ontology_api.routes.proteins.proteins_controller import proteins_blueprint
from hs_ontology_api.routes.proteinsinfo.proteinsinfo_controller import proteinsinfo_blueprint
from hs_ontology_api.routes.celltypes.celltypes_controller import celltypes_blueprint
from hs_ontology_api.routes.celltypesinfo.celltypesinfo_controller import celltypesinfo_blueprint
from hs_ontology_api.routes.fielddescriptions.fielddescriptions_controller import field_descriptions_blueprint
from hs_ontology_api.routes.fieldtypes.fieldtypes_controller import field_types_blueprint
from hs_ontology_api.routes.fieldassays.fieldassays_controller import field_assays_blueprint
from hs_ontology_api.routes.fieldschemas.fieldschemas_controller import field_schemas_blueprint
from hs_ontology_api.routes.fieldtypesinfo.fieldtypesinfo_controller import field_types_info_blueprint
from hs_ontology_api.routes.fieldentities.fieldentities_controller import field_entities_blueprint
from hs_ontology_api.routes.assayclasses.assayclasses_controller import assayclasses_blueprint
from hs_ontology_api.routes.datasettypes.datasettypes_controller import datasettypes_blueprint
from hs_ontology_api.routes.modalities.modalities_controller import modalities_blueprint
from hs_ontology_api.routes.analytes.analytes_controller import analytes_blueprint
from hs_ontology_api.routes.pathways.pathways_controller import pathways_blueprint
from hs_ontology_api.routes.annotations.annotations_controller import annotations_blueprint

def make_flask_config():
    """
    Used to override the "native" app.cfg for the ubkg-api instantiated by the child API with
    values from the child API.
    """
    temp_flask_app = Flask(__name__,
                      instance_path=path.join(path.abspath(path.dirname(__file__)), 'hs_ontology_api/instance'),
                      instance_relative_config=True)
    temp_flask_app.config.from_pyfile('app.cfg')
    return temp_flask_app.config

# -------- START

# Overwrite the ubkg-api's app configuration with the configuration from hs-ontology-api.
cfg = make_flask_config()
app = UbkgAPI(cfg, Path(__file__).absolute().parent.parent).app
app.config = cfg

app.register_blueprint(organs_blueprint)
app.register_blueprint(relationships_blueprint)
app.register_blueprint(valueset_blueprint)
app.register_blueprint(genes_blueprint)
app.register_blueprint(genesinfo_blueprint)
app.register_blueprint(proteins_blueprint)
app.register_blueprint(proteinsinfo_blueprint)
app.register_blueprint(celltypesinfo_blueprint)
app.register_blueprint(celltypes_blueprint)
app.register_blueprint(field_descriptions_blueprint)
app.register_blueprint(field_types_blueprint)
app.register_blueprint(field_assays_blueprint)
app.register_blueprint(field_schemas_blueprint)
app.register_blueprint(field_types_info_blueprint)
app.register_blueprint(field_entities_blueprint)
app.register_blueprint(assayclasses_blueprint)
app.register_blueprint(datasettypes_blueprint)
app.register_blueprint(modalities_blueprint)
app.register_blueprint(analytes_blueprint)
app.register_blueprint(pathways_blueprint)
app.register_blueprint(annotations_blueprint)

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

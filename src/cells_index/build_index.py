# coding: utf-8

# Prototype utility that builds a CSV file of information extracted from the Cells API.
# This script is not part of the Flask Blueprint architecture, but shares the app.cfg file.

import logging
import csv
import os

# Cells API client
from hubmap_api_py_client import Client
from hubmap_api_py_client.errors import ClientError

from flask import Flask

# Instantiate hubmap-api-py-client. Obtain URL from the Flask app's config file.
def make_flask_config():
    temp_flask_app = Flask(__name__,
                      instance_path=os.path.join(os.path.dirname(os.getcwd()), 'hs_ontology_api/instance'),
                      instance_relative_config=True)
    temp_flask_app.config.from_pyfile('app.cfg')
    return temp_flask_app.config

# ---

logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)
logger = logging.getLogger(__name__)
client_url = make_flask_config()['CELLSURL']
client = Client(client_url)

# Open CSV and write header.
fpath = os.path.dirname(os.getcwd())
fpath = os.path.join(fpath, 'cells_index/cells.tsv')
csvfile = open(fpath, 'w', newline='')
cellwriter = csv.writer(csvfile, delimiter='\t',quotechar='|', quoting=csv.QUOTE_MINIMAL)
cellwriter.writerow(['gene_symbol', 'dataset_uuid', 'organ', 'cell_type'])

# Load dataset and cell information using Cells API.

# 1. All datasets
datasets = client.select_datasets()
logging.info(f'{len(datasets)} datasets')

# 2. All cells in datasets.
dataset_uuids = []
datasets = datasets.get_list()
for d in datasets:
    dataset_uuids.append(d['uuid'])

cells_in_datasets = client.select_cells(where='dataset', has=dataset_uuids)
logging.info(f'{len(cells_in_datasets)} cells in datasets')

# 3. All genes
genes = client.select_genes().get_list()
logging.info(f'{len(genes)} genes')

# DEBUG - use set of test genes for prototype.
genes = [{'gene_symbol':'MMRN1'}]
# Check every gene for presence in cells in datasets.
gene_symbols = []

for gene in genes:
    gene_symbol = gene['gene_symbol']
    try:
        # Find cells with the gene, and intersect with cells from datasets to find
        # cells with the gene in datasets.
        logging.info(f'Looking for cells with gene {gene_symbol}, rna')
        cells_with_gene_rna = client.select_cells(where='gene', has=[f'{gene_symbol} > 1'], genomic_modality='rna')
        logging.info(f'Looking for cells with gene {gene_symbol}, atac')
        cells_with_gene_atac = client.select_cells(where='gene', has=[f'{gene_symbol} > 1'], genomic_modality='atac')

        # Cells from all modalities
        cells_with_gene = cells_with_gene_rna | cells_with_gene_atac

        # Cells with gene in datasets
        cells_with_gene_in_datasets = cells_with_gene & cells_in_datasets
        cells_list = cells_with_gene_in_datasets.get_list()

        # Find distinct combinations of cell type, dataset, gene.
        cell_types = []
        for c in cells_list:
            cell_type = c['cell_type']
            if not cell_type in cell_types:
                cell_types.append(cell_type)
                dataset_uuid = c['dataset']
                organ = c['organ']
                cellwriter.writerow([gene_symbol, dataset_uuid, organ, cell_type])

    except ClientError:
        # The genes list contains elements that are not actually genes, and that
        # result in errors from the client that are meaningless in this context.
        pass
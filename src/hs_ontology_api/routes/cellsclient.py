# coding: utf-8
# JAS October 2023

# Wrapper for the Cells client (hubmap-api-py-client).

from hubmap_api_py_client import Client
from hubmap_api_py_client.errors import ClientError

class OntologyCellsClient():

    def __init__(self):

        # Obtains relatively invariant data from Cells API regarding datasets, cells, and genes.

        # Instantiate hubmap-api-py-client.
        self.client_url = 'https://cells.dev.hubmapconsortium.org/api/'
        self.client = Client(self.client_url)

        # Load dataset and cell information using Cells API.
        # These objects will be used in set operations to identify genes.

        # All datasets
        self.datasets = self.client.select_datasets()
        print(f'{len(self.datasets)} datasets')

        # All cells in datasets.
        dataset_uuids = self.datasets.get_list().keys
        for d in self.datasets.get_list():
            dataset_uuids.append(d['uuid'])

        self.cells_in_datasets = self.client.select_cells(where='dataset', has=dataset_uuids)
        print(f'{len(self.cells_in_datasets)} cells in datasets')

        # All genes
        self.genes = self.client.select_genes().get_list()
        print(f'{len(self.genes)} genes')

    def genes_from_cells(self) -> list[str]:

        # Returns a list of HGNC IDs for genes that have been identified in cells in datasets.

        gene_symbols = []
        testcount = 0

        # Check every gene for presence in cells in datasets
        for gene in self.genes:
            gene_symbol = gene['gene_symbol']
            try:
                cells_with_gene = self.client.select_cells(where='gene', has=[f'{gene_symbol} > 0.5'], genomic_modality='rna')

                # The cells_in_datasets object was instantiated at API startup.
                cells_with_gene_in_datasets = cells_with_gene & self.cells_in_datasets

                cells_list = cells_with_gene_in_datasets.get_list()
                if len(cells_list) > 0:
                    print(f'{gene_symbol} is in cells in datasets')
                    gene_symbols.append(gene_symbol)
                testcount = testcount + 1
                if testcount > 4: # For debugging, because there are over 60K "genes" in list
                    break
            except ClientError:
                print(f'{gene_symbol}: error')
                pass

        return gene_symbols

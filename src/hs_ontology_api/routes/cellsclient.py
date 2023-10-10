# coding: utf-8
# JAS October 2023

# Wrapper for the Cells client (hubmap-api-py-client).
import logging

from hubmap_api_py_client import Client
from hubmap_api_py_client.errors import ClientError

import csv

class OntologyCellsClient():

    def __init__(self):

        logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s:%(lineno)d: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        #self.logger.info(f'Startup: getting preliminary information from Cells API...')

        # Instantiate hubmap-api-py-client.
        self.client_url = 'https://cells.dev.hubmapconsortium.org/api/'
        self.client = Client(self.client_url)

    def celltypes_for_gene(self, gene_symbol: str) -> list[str]:

        """
        Returns a list of Cell Ontology identifiers for cell types of cells that associate with a gene.
        :param gene_symbol: approved HGNC gene symbol
        :return: List[str]
        """

        logging.info('celltypes_for_gene')
        try:
            cells_with_gene = self.client.select_cells(where='gene', has=[f'{gene_symbol} > 1'],
                                                       genomic_modality='rna').get_list()
            cell_type_names = []
            for c in cells_with_gene:
                if not c['cell_type'] in cell_type_names:
                    cell_type_names.append(c['cell_type'])
            return cell_type_names
        except ClientError:
            # The client returns an error if a "gene" is not in a list internal to the client.
            self.logger.info(f'{gene_symbol}: error')
            return []




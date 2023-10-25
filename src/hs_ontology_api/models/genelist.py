# coding: utf-8

# JAS October 2023
# GeneList model class
# Used by the geneslist endpoint.
# Provides information on genes identified by either the UBKG or the Cells API--i.e., that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

# Sub-object models
# Array of gene detail objects
from hs_ontology_api.models.genelist_detail import GeneListDetail

class GeneList():
    def __init__(self, page=None, total_pages=None, genesperpage=None, genes=None, starts_with=None, gene_count=None):
        """GeneList - a model defined in OpenAPI

                    :param page: Relative "page" (block of genes)
                    :type page: str
                    :param total_pages: Total number of "pages" (blocks of genes)
                    :type total_pages: str
                    :param genes: List of genes in page
                    :type genes: List[GeneListDetail]
                    :param genesperpage: Number of genes in each "page" (block)
                    :type genes: str
                    :starts_with: Search string for type ahead
                    :type starts_with: str
                    :gene_count: Count of (filtered) genes
                    :type gene_count: str


                """

        # Parameters other than page will be used to build nested GeneListDetail objects.

        # Types for JSON objects
        self.openapi_types = {
            'page': int,
            'total_pages': int,
            'genes_per_page': int,
            'genes': List[GeneListDetail],
            'starts_with': str,
            'gene_count': int
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'page': 'page',
            'total_pages': 'total_pages',
            'genes_per_page': 'genes_per_page',
            'genes': 'genes',
            'starts_with': 'starts_with',
            'gene_count': 'gene_count'
        }
        # Property assignments
        self._page = int(page)
        self._total_pages = int(total_pages)
        self._genes_per_page = int(genesperpage)
        self._genes = genes
        self._starts_with = starts_with
        self._gene_count = gene_count

    def serialize(self):
        # Key/value format of response.
        return {
            "page": self._page,
            "total_pages": self._total_pages,
            "genes_per_page": self._genes_per_page,
            "genes": self._genes,
            "starts_with": self._starts_with,
            "gene_count": self._gene_count
        }

    @classmethod
    def from_dict(cls, dikt) -> 'GeneList':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetail of this GeneDetail
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def page(self):
        """Gets the page of this GeneList.

        'Page' or relative block of genes.
        :return: The page of this GeneList.
        :rtype: str
        """
        return self._page

    @page.setter
    def page(self, page):
        """Sets the page of this GeneList.

        'Page' or relative block of genes.

        :param page: The page of this GeneList
        :type page: str
        """

        self._page = page

    @property
    def genes(self):
        """Gets the genes of this GeneList.

        Gene list.
        :return: The genes of this GeneList.
        :rtype: List[GeneListDetail]
        """
        return self._genes

    @genes.setter
    def genes(self, genes):
        """Sets the genes of this GeneList.

        Gene list

        :param genes: The genes of this GeneList
        :type genes: str
        """

        self._genes = genes

    @property
    def total_pages(self):
        """Gets the total_pages of this GeneList.

        Total number of "pages" (blocks of genes)
        :return: The total_pages of this GeneList.
        :rtype: int
        """
        return self._total_pages

    @total_pages.setter
    def total_pages(self, total_pages):
        """Sets the total_pages of this GeneList.

        Total number of "pages" (blocks of genes)

        :param total_pages: The genes of this GeneList
        :type genes: int
        """

        self._total_pages = total_pages

    @property
    def genes_per_page(self):
        """Gets the genes_per_page of this GeneList.

        Number of genes per "page" or block of returns
        :return: The total_pages of this GeneList.
        :rtype: int
        """
        return self._total_pages

    @genes_per_page.setter
    def genes_per_page(self, genes_per_page):
        """Sets the genes_per_page of this GeneList.

        Number of genes per "page" or block of returns

        :param genes_per_page: The genes_per_page of this GeneList
        :type genes_per_page: int
        """

        self._genes_per_page = genes_per_page
    @property
    def starts_with(self):
        """Gets the starts_with of this GeneList.

        Optional type-ahead search string
        :return: The starts_with of this GeneList.
        :rtype: str
        """
        return self._starts_with

    @starts_with.setter
    def starts_with(self, starts_with):
        """Sets the starts_with of this GeneList.

        Optional type-ahead search string

        :param starts_with: The genes_per_page of this GeneList
        :type starts_with: int
        """

        self._starts_with = starts_with
    @property
    def gene_count(self):
        """Gets the gene_count of this GeneList.

        Count of genes
        :return: The gene_count of this GeneList.
        :rtype: str
        """
        return self._gene_count

    @gene_count.setter
    def gene_count(self, gene_count):
        """Sets the gene_count of this GeneList.

        Count of genes

        :param gene_count: The gene_count of this GeneList
        :type gene_count: int
        """

        self._gene_count = gene_count

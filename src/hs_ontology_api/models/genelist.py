# coding: utf-8

# JAS October 2023
# GeneList model class
# Used by the genes-info endpoints.
# Provides information on genes identified by either the UBKG or the Cells API--i.e., that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

# Sub-object models
# Array of gene detail objects
from hs_ontology_api.models.genelist_detail import GeneListDetail
from hs_ontology_api.models.pagination import Pagination

class GeneList():
    def __init__(self, page=None, totalpages=None, genesperpage=None, genes=None, startswith=None, genecount=None):
        """GeneList - a model defined in OpenAPI

                    :param page: Requested relative "page" (block of genes)
                    :type page: str
                    :param totalpages: Calculated total number of "pages" (blocks of genes)
                    :type totalpages: str
                    :param genes: List of gene objects for an array
                    :type genes: List[GeneListDetail]
                    :param genesperpage: Requested number of genes in each "page" (block)
                    :type genesperpage: str
                    :startswith: Optional search string for type ahead
                    :type startswith: str
                    :genecount: Calculated count of genes that satisfied the search criteria
                    :type genecount: str

                """

        # The page, totalpages, genesperpage, startswith, and genecount parameters will be used to build a
        # Pagination object.
        # The genes parameter will be used to build an array of GeneListDetail objects.

        # Types for JSON objects
        self.openapi_types = {
            'pagination': Pagination,
            'genes': List[GeneListDetail],
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'pagination': 'pagination',
            'genes': 'genes',
        }
        # Property assignments
        self._genes = genes
        self._pagination = Pagination(page, totalpages, genesperpage, startswith, genecount).serialize()

    def serialize(self):
        # Key/value format of response.
        return {
            "pagination": self._pagination,
            "genes": self._genes,
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
    def pagination(self):
        """Gets the pagination of this GeneList.

        Pagination statistics
        :return: The pagination of this GeneList.
        :rtype: str
        """
        return self._pagination

    @pagination.setter
    def pagination(self, pagination):
        """Sets the pagination of this GeneList.

        Pagination statistics
        :param pagination: The pagination of this GeneList
        :type pagination: str
        """

        self._pagination = pagination

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


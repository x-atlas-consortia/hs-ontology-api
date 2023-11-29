# coding: utf-8

# JAS November 2023
# CelltypeList model class
# Used by the celltypes-info endpoints.
# Provides information on celltypes identified by either the UBKG or the Cells API--i.e.,
# that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
from typing import List
# from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

# Sub-object models
# Array of gene detail objects
#from hs_ontology_api.models.genelist_detail import GeneListDetail
from hs_ontology_api.models.pagination import Pagination

class CelltypeList:
    def __init__(self, page=None, total_pages=None, cell_types_per_page=None, cell_types=None, starts_with=None, cell_type_count=None):
        """CelltypeList - a model defined in OpenAPI

                    :param page: Requested relative "page" (block of genes)
                    :type page: str
                    :param total_pages: Calculated total number of "pages" (blocks of cell types)
                    :type total_pages: str
                    :param cell_types: List of cell type objects for an array
                    :type cell_types: List[CelltypeListDetail]
                    :param cell_types_per_page: Requested number of cell types in each "page" (block)
                    :type cell_types_per_page: str
                    :starts_with: Optional search string for type ahead
                    :type starts_with: str
                    :cell_type_count: Calculated count of cell types that satisfied the search criteria
                    :type cell_type_count: str

                """

        # The page, total_pages, celltypes_per_page, starts_with, and cell_type_count parameters will be used to build a
        # Pagination object.
        # The cell_types parameter will be used to build an array of CelltypeListDetail objects.

        # Types for JSON objects
        self.openapi_types = {
            'pagination': Pagination,
            #'cell_types': List[CelltypeListDetail],
            'cell_types': List[str]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'pagination': 'pagination',
            'cell_types': 'cell_types',
        }
        # Property assignments
        self._cell_types = cell_types
        self._pagination = Pagination(page=page, total_pages=total_pages, items_per_page=cell_types_per_page,
                                      starts_with=starts_with, item_count=cell_type_count).serialize()

    def serialize(self):
        # Key/value format of response.
        return {
            "pagination": self._pagination,
            "cell_types": self._cell_types,
        }

    @classmethod
    def from_dict(cls, dikt) -> 'CelltypeList':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CelltypeList of this CelltypeList
        :rtype: CelltypeList
        """
        return util.deserialize_model(dikt, cls)

    @property
    def pagination(self):
        """Gets the pagination of this CelltypeList.

        Pagination statistics
        :return: The pagination of this CelltypeList.
        :rtype: str
        """
        return self._pagination

    @pagination.setter
    def pagination(self, pagination):
        """Sets the pagination of this CelltypeList.

        Pagination statistics
        :param pagination: The pagination of this CelltypeList
        :type pagination: str
        """

        self._pagination = pagination

    @property
    def cell_types(self):
        """Gets the cell_types of this CelltypeList.

        Gene list.
        :return: The cell_types of this CelltypeList.
        :rtype: List[CelltypeListDetail]
        """
        return self._cell_types

    @cell_types.setter
    def cell_types(self, cell_types):
        """Sets the cell_types of this CelltypeList.

        Cell type list

        :param cell_types: The cell_types of this CelltypeList
        :type cell_types: str
        """

        self._cell_types = cell_types

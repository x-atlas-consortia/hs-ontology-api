# coding: utf-8

# JAS Nov 2023
# ProteinList model class
# Used by the proteins-info endpoints.
# Provides information on proteins identified by either the UBKG or the Cells API--i.e., that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

# Sub-object models
# Array of protein detail objects
from hs_ontology_api.models.proteinlist_detail import ProteinListDetail
from hs_ontology_api.models.pagination import Pagination

class ProteinList():
    def __init__(self, page=None, total_pages=None, proteins_per_page=None, proteins=None, starts_with=None, protein_count=None):
        """ProteinList - a model defined in OpenAPI

                    :param page: Requested relative "page" (block of proteins)
                    :type page: str
                    :param total_pages: Calculated total number of "pages" (blocks of proteins)
                    :type total_pages: str
                    :param protei: List of protein objects for an array
                    :type proteins: List[GeneListDetail]
                    :param proteins_per_page: Requested number of proteins in each "page" (block)
                    :type proteins_per_page: str
                    :starts_with: Optional search string for type ahead
                    :type starts_with: str
                    :protein_count: Calculated count of proteins that satisfied the search criteria
                    :type protein_count: str

                """

        # The page, total_pages, proteins_per_page, starts_with, and proteins_count parameters will be used to build a
        # Pagination object.
        # The proteins parameter will be used to build an array of GeneListDetail objects.

        # Types for JSON objects
        self.openapi_types = {
            'pagination': Pagination,
            'proteins': List[ProteinListDetail],
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'pagination': 'pagination',
            'proteins': 'proteins',
        }
        # Property assignments
        self._proteins = proteins
        self._pagination = Pagination(page=page, total_pages=total_pages, items_per_page=proteins_per_page,
                                      starts_with=starts_with, item_count=protein_count).serialize()

    def serialize(self):
        # Key/value format of response.
        return {
            "pagination": self._pagination,
            "proteins": self._proteins,
        }

    @classmethod
    def from_dict(cls, dikt) -> 'ProteinList':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ProteinDetail of this ProteinDetail
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def pagination(self):
        """Gets the pagination of this ProteinList.

        Pagination statistics
        :return: The pagination of this ProteinList.
        :rtype: str
        """
        return self._pagination

    @pagination.setter
    def pagination(self, pagination):
        """Sets the pagination of this ProteinList.

        Pagination statistics
        :param pagination: The pagination of this ProteinList
        :type pagination: str
        """

        self._pagination = pagination

    @property
    def proteins(self):
        """Gets the proteins of this ProteinList.

        Protein list.
        :return: The proteins of this ProteinList.
        :rtype: List[ProteinListDetail]
        """
        return self._proteins

    @proteins.setter
    def proteins(self, proteins):
        """Sets the proteins of this ProteinList.

        Gene list

        :param proteins: The proteins of this ProteinList
        :type proteins: str
        """

        self._proteins = proteins


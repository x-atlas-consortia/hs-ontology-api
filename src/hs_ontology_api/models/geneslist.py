# coding: utf-8

# JAS October 2023
# GenesList model class
# Used by the geneslist endpoint.
# Provides information on genes identified by either the UBKG or the Cells API--i.e., that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class GenesList(Model):
    def __init__(self, hgnc_id=None, approved_symbol=None, approved_name=None, description=None, page=None):
        """GenesList - a model defined in OpenAPI

            :param hgnc_id: hgnc ID
            :type hgnc_id: str
            :param approved_symbol: approved symbol
            :type approved_symbol: str
            :param approved_name: approved name
            :type approved_name: str
            :param description: RefSeq description
            :type description: str
            :param page: page offset
            :type page: str

        """
        # Types for JSON objects
        self.openapi_types = {
            'hgnc_id': str,
            'approved_symbol': str,
            'approved_name': str,
            'description': str,
            'page':int
        }

        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'hgnc_id': 'hgnc_id',
            'approved_symbol': 'approved_symbol',
            'approved_name': 'approved_name',
            'description': 'description',
            'page':'page'
        }

        # Property assignments
        self._hgnc_id = hgnc_id
        self._page = int(page)
        if approved_symbol is None:
            self._approved_symbol = ''
        else:
            self._approved_symbol = approved_symbol[0]

        if approved_name is None:
            self._approved_name = ''
        else:
            self._approved_name = approved_name[0]

        self._description = description

    def serialize(self):
        # Key/value format of response.
        return {
            "hgnc_id": self._hgnc_id,
            "approved_symbol": self._approved_symbol,
            "approved_name": self._approved_name,
            "description": self._description,
            "page": self._page
        }

    @classmethod
    def from_dict(cls, dikt) -> 'GenesList':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetail of this GenesFromCells
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def hgnc_id(self):
        """Gets the hgnc_id of this GenesList.

        Current HGNC approved id for the gene.
        :return: The hgnc_id of this GeneDetail.
        :rtype: str
        """
        return self._hgnc_id

    @hgnc_id.setter
    def hgnc_id(self, hgnc_id):
        """Sets the hgnc_id of this GenesList.

        Current HGNC approved id for the gene.

        :param hgnc_id: The hgnc_id of this gene
        :type approved_id: str
        """

        self._hgnc_id = hgnc_id

    @property
    def approved_symbol(self):
        """Gets the approved_symbol of this GenesList.

        Current HGNC approved symbol for the gene.
        :return: The approved_symbol of this GenesList.
        :rtype: str
        """
        return self._approved_symbol

    @approved_symbol.setter
    def approved_symbol(self, approved_symbol):
        """Sets the approved_symbol of this GenesList.

        Current HGNC approved symbol for the gene.

        :param approved_symbol: The approved symbol of this Gene
        :type approved_symbol: str
        """

        self._approved_symbol = approved_symbol

    @property
    def approved_name(self):
        """Gets the approved_name of this GenesList.

        Current HGNC approved name for the gene.
        :return: The approved_name of this GenesList.
        :rtype: str
        """
        return self._approved_name

    @approved_name.setter
    def approved_name(self, approved_name):
        """Sets the approved_name of this GenesList.

        Current HGNC approved name for the gene.

        :param approved_name: The approved_name of this Gene
        :type approved_name: str
        """

        self._approved_name = approved_name

    @property
    def description(self):
        """Gets the description of this GenesList.

        RefSeq summary for the gene.
        :return: The description of this GenesList.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this GenesList.

       RefSeq summary for the gene.

        :param description: The description of this Gene
        :type description: str
        """

        self._description = description

    @property
    def page(self):
        """Gets the page of this GenesList.

        Offset page.
        :return: The page of this GenesList.
        :rtype: int
        """
        return self._page

    @description.setter
    def description(self, page):
        """Sets the page of this GenesList.

       Offset page.

        :param page: The description of this Gene
        :type description: int
        """

        self._page = page
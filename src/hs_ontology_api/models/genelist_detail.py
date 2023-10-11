# coding: utf-8

# JAS October 2023
# GenesListDetail model class
# Used by the geneslist endpoint.
# Provides information on genes identified by either the UBKG or the Cells API--i.e., that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class GeneListDetail(Model):
    def __init__(self, hgnc_id=None, approved_symbol=None, approved_name=None, summary=None):
        """GenesListDetail - a model defined in OpenAPI

            :param hgnc_id: hgnc ID
            :type hgnc_id: str
            :param approved_symbol: approved symbol
            :type approved_symbol: str
            :param approved_name: approved name
            :type approved_name: str
            :param summary: RefSeq description
            :type summary: str

        """
        # Types for JSON objects
        self.openapi_types = {
            'hgnc_id': str,
            'approved_symbol': str,
            'approved_name': str,
            'summary': str
        }

        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'hgnc_id': 'hgnc_id',
            'approved_symbol': 'approved_symbol',
            'approved_name': 'approved_name',
            'summary': 'summary'
        }

        # Property assignments
        self._hgnc_id = hgnc_id
        if approved_symbol is None:
            self._approved_symbol = ''
        else:
            self._approved_symbol = approved_symbol[0]

        if approved_name is None:
            self._approved_name = ''
        else:
            self._approved_name = approved_name[0]

        if summary is None:
            self._summary = ''
        else:
            self._summary = summary[0]

    def serialize(self):
        # Key/value format of response.
        return {
            "hgnc_id": self._hgnc_id,
            "approved_symbol": self._approved_symbol,
            "approved_name": self._approved_name,
            "summary": self._summary,
        }

    @classmethod
    def from_dict(cls, dikt) -> 'GenesListDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetail of this GenesFromCells
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def hgnc_id(self):
        """Gets the hgnc_id of this GenesListDetail.

        Current HGNC approved id for the gene.
        :return: The hgnc_id of this GeneListDetail.
        :rtype: str
        """
        return self._hgnc_id

    @hgnc_id.setter
    def hgnc_id(self, hgnc_id):
        """Sets the hgnc_id of this GeneListDetail.

        Current HGNC approved id for the gene.

        :param hgnc_id: The hgnc_id of this gene
        :type approved_id: str
        """

        self._hgnc_id = hgnc_id

    @property
    def approved_symbol(self):
        """Gets the approved_symbol of this GeneListDetail.

        Current HGNC approved symbol for the gene.
        :return: The approved_symbol of this GeneListDetail.
        :rtype: str
        """
        return self._approved_symbol

    @approved_symbol.setter
    def approved_symbol(self, approved_symbol):
        """Sets the approved_symbol of this GenesListDetail.

        Current HGNC approved symbol for the gene.

        :param approved_symbol: The approved symbol of this Gene
        :type approved_symbol: str
        """

        self._approved_symbol = approved_symbol

    @property
    def approved_name(self):
        """Gets the approved_name of this GenesListDetail.

        Current HGNC approved name for the gene.
        :return: The approved_name of this GenesList.
        :rtype: str
        """
        return self._approved_name

    @approved_name.setter
    def approved_name(self, approved_name):
        """Sets the approved_name of this GenesListDetail.

        Current HGNC approved name for the gene.

        :param approved_name: The approved_name of this Gene
        :type approved_name: str
        """

        self._approved_name = approved_name

    @property
    def summary(self):
        """Gets the summary of this GenesListDetail.

        RefSeq summary for the gene.
        :return: The summary of this GenesListDetail.
        :rtype: str
        """
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Sets the summary of this GenesListDetail.

       RefSeq summary for the gene.

        :param summary: The description of this Gene
        :type summary: str
        """

        self._summary = summary

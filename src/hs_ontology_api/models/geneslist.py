# coding: utf-8

# JAS October 2023
# GenesFromCells model class
# Used by the genesfromcells endpoint.
# Provides information on genes identified by the Cells API--i.e., that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class GenesList(Model):
    def __init__(self, hgnc_ids=None):
        """GenesList - a model defined in OpenAPI

            :param hgnc_ids: list of HGNC IDs for genes identified by Cells
            :type hgnc_ids: List[str]

        """
        # Types for JSON objects
        self.openapi_types = {
            'hgnc_ids': List[str]
        }

        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'hgnc_ids': 'hgnc_ids'
        }

        # Property assignments
        self._hgnc_ids = hgnc_ids

    def serialize(self):
        # Key/value format of response.
        return {
            "hgnc_ids": self._hgnc_ids
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
    def hgnc_ids(self):
        """Gets the hgnc_id of this GenesFromCells.

        Current HGNC approved id for the gene.
        :return: The hgnc_id of this GeneDetail.
        :rtype: str
        """
        return self._hgnc_ids

    @hgnc_ids.setter
    def hgnc_ids(self, hgnc_ids):
        """Sets the hgnc_id of this GenesFromCells.

        Current HGNC approved id for the gene.

        :param hgnc_id: The hgnc_id of this Gene
        :type approved_id: str
        """

        self._hgnc_ids = hgnc_ids

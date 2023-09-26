# coding: utf-8

# JAS September 2023
# GeneDetail model
# Information on a gene identified in HGNC.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


class GeneDetail(Model):
    def __init__(self, approved_symbol=None):
        """GeneDetail - a model defined in OpenAPI

                :param approved_symbol: HGNC current approved symbol for the gene
                :type approved_symbol: str

        """
        self.openapi_types = {
            'approved_symbol': str
        }
        self.attribute_map = {
            'approved_symbol': 'approved_symbol',
        }
        self._approved_symbol = approved_symbol

    def serialize(self):
        return {
            "approved_symbol": self._approved_symbol
        }

    @classmethod
    def from_dict(cls, dikt) -> 'GeneDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetail of this GeneDetail
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def approved_symbol(self):
        """Gets the approved_symbol of this GeneDetail.

        Current HGNC approved symbol for the gene.
        :return: The approved_symbol of this GeneDetail.
        :rtype: str
        """
        return self.approved_symbol

    @approved_symbol.setter
    def approved_symbol(self, approved_symbol):
        """Sets the approved_symbol of this GeneDetail.

        Current HGNC approved symbol for the gene.

        :param approved_symbol: The approved_symbol of this GeneInfo
        :type approved_symbol: str
        """

        self._approved_symbol = approved_symbol


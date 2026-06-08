# coding: utf-8

# JAS September 2023
# GeneDetailCellTypes model
# Information on the organs associated with cell types associated with a gene identified in HGNC.

from __future__ import absolute_import
# from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


class GeneDetailCellTypeOrgan(Model):
    def __init__(self, source=None, id=None, name=None):
        """GeneDetailCellType - a model defined in OpenAPI
            :param source: source vocabulary for an organ reference (e.g., UBERON)
            :type source: str
            :param id: id for organ reference (e.g.,0000948)
            :type source: str
            :param name: name for organ reference (e.g.,heart)
        """
        # The parameter organ_list will be decomposed into key/value pairs.
        # types
        self.openapi_types = {
            'id': str,
            'source': str,
            'name': str
        }
        # attributions
        self.attribute_map = {
            'id': 'id',
            'source': 'source',
            'name': 'name'
        }
        # assignments

        self._id = id
        self._source = source
        self._name = name

    def serialize(self):
        # Key/value formatting for response.
        return {
            "id": self._id,
            "source": self._source,
            "name": self._name
        }

    @classmethod
    def from_dict(cls, dikt) -> 'GeneDetailCellTypeOrgan':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetailCellTypeOrgan of this GeneDetailCellTypeOrgan
        :rtype: GeneDetailCellTypeOrgan
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this GeneDetailCellTypeOrgan.

        ID for the organ
        :return: id for the organ
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the code of this GeneDetailCellTypeOrgan.

        ID for the organ

        :param id: The organ ID
        :type id: str
        """

        self._id = id

    @property
    def source(self):
        """Gets the source of this GeneDetailCellTypeOrgan.

        source for the organ
        :return: source for the organ reference
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this GeneDetailCellTypeOrgan.

        Source for the organ reference

        :param source: source
        :type source: str
        """

        self._source = source

    @property
    def name(self):
        """Gets the name of this GeneDetailCellTypeOrgan.

        name for the organ reference
        :return: source
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the noame of this GeneDetailCellTypeOrgan.

        name for the organ reference

        :param name: The CL code
        :type name: str
        """

        self._name = name


# coding: utf-8

# JAS September 2023
# GeneDetailCellTypes model
# Information on the cell types associated with gene identified in HGNC.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class GeneDetailCellType(Model):
    def __init__(self, id=None, name=None):
        """GeneDetailCellType - a model defined in OpenAPI
            :param id: the code in Cell Ontology that HRA indicates is associated with a gene (in format CL:CODE)
            :type id: str
            :param name: the preferred term for the cell type in Cell Ontology
            :type id: str

        """
        self.openapi_types = {
            'id': str,
            'name': str
        }
        self.attribute_map = {
            'id': 'id',
            'name': 'name'
        }
        self._id = id
        self._name = name

    def serialize(self):
        # Key/value formatting for response.
        return {
            "id": self._id,
            "name": self._name

        }

    @classmethod
    def from_dict(cls, dikt) -> 'GeneDetailCellType':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetailReference of this GeneDetailCellType
        :rtype: GeneDetailReference
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this GeneDetailCellType.

        ID for the reference
        :return: CL code
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the code of this GeneDetailCellType.

        Code for the cell type

        :param id: The CL code
        :type id: str
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this GeneDetailCellType.

        name for the cell type
        :return: name for the reference
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this GeneDetailCellType.

        Name for the CL code

        :param name: The CL name
        :type name: str
        """

        self._name = name

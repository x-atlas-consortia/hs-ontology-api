# coding: utf-8

# JAS December 2023
# FieldDescription model class
# Used by the field-descriptions endpoint.
# Replicates read of legacy field_descriptions.yaml.

from __future__ import absolute_import
from typing import List
# from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class FieldDescription:
    def __init__(self, codeID=None, identifier=None, description=None):
        """
        FieldDescription - a model defined in OpenAPI

        Represents a code from the HMFIELD ontology.
        :param codeID: codeID for the Code node in HMFIELD
        :param identifier: equivalent of the field key in the yaml
        :param description: description

        example:
        codeID - HMFIELD:1001
        identifier - ablation_distance_between_shots_x_units
        description - Units of x resolution distance between laser ablation shots.

        """

        # Types for JSON objects
        self.openapi_types = {
            'codeID': str,
            'identifier': str,
            'description:': str
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'codeID': 'codeID',
            'identifier': 'identifier',
            'description': 'description'
        }
        # Property assignments
        self._codeID = codeID
        self._identifier = identifier
        self._description = description

    def serialize(self):
        # Key/value format of response.
        return {
            "codeID": self._codeID,
            "identifier": self._identifier,
            "description": self._description
        }

    @classmethod
    def from_dict(cls, dikt) -> 'FieldDescription':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The FieldDescription of this FieldDescription
        :rtype: FieldDescription
        """
        return util.deserialize_model(dikt, cls)

    @property
    def codeID(self):
        """Gets the codeID of this FieldDescription.
        :return: The codeID for the field from HMFIELD
        :rtype: str
        """
        return self._codeID

    @codeID.setter
    def codeID(self, codeID):
        """Sets the codeID for the field from HMFIELD

        :param codeID: The codeID of this field
        :type codeID: str
        """
        self._codeID = codeID

    @property
    def identifier(self):
        """Gets the identifier of this FieldDescription.
        :return: The identifier for the field
        :rtype: str
        """
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        """Sets the identifier for the field from HMFIELD

        :para identifier: The identifier of this field
        :type identifier: str
        """
        self._identifier = identifier

    @property
    def description(self):
        """Gets the description of this FieldDescription.
        :return: The description for the field from HMFIELD
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description for the field from HMFIELD

        :param description: The description of this field
        :type description: str
        """
        self._description = description
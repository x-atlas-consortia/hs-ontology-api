# coding: utf-8

# JAS December 2023
# FieldType model class
# Used by the field-types endpoint.
# Replicates read of legacy field_types.yaml.

from __future__ import absolute_import
# from typing import List
# from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


class FieldType:
    def __init__(self, codeID=None, identifier=None, hm_type=None, xsd_type=None):
        """
        FieldType - a model defined in OpenAPI

        Represents a code from the HMFIELD ontology.
        :param codeID: codeID for the Code node in HMFIELD
        :param identifier: equivalent of the field key in the yaml
        :param hm_type: field type from legacy field_types.yaml
        :param xsd_type: corresponding field type for field in XSD

        example:
        codeID - HMFIELD:1001
        identifier - ablation_distance_between_shots_x_units
        hm_type - string
        xsd_type: xsd:string

        """

        # Types for JSON objects
        self.openapi_types = {
            'codeID': str,
            'identifier': str,
            'type:': dict
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'codeID': 'codeID',
            'identifier': 'identifier',
            'type': 'type'
        }
        # Property assignments
        self._codeID = codeID
        if identifier is None:
            self._identifier = ''
        else:
            self._identifier = identifier
        dicttype = {}
        if hm_type is not None:
            dicttype['name'] = hm_type
        if xsd_type is not None:
            dicttype['XSDcode'] = xsd_type
        self._type = dicttype

    def serialize(self):
        # Key/value format of response.
        return {
            "codeID": self._codeID,
            "identifier": self._identifier,
            "type": self._type
        }

    @classmethod
    def from_dict(cls, dikt) -> 'FieldType':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The FieldType of this FieldType
        :rtype: FieldType
        """
        return util.deserialize_model(dikt, cls)

    @property
    def codeID(self):
        """Gets the codeID of this FieldType.
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
        """Gets the identifier of this FieldType.
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
    def type(self):
        """Gets the type of this FieldType.
        :return: The type for the field from HMFIELD
        :rtype: dict
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the description for the field from HMFIELD

        :param type: The description of this field
        :type type: dict
        """
        self._type = type

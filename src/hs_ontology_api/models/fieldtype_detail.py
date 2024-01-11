# coding: utf-8

# JAS January 2024
# FieldTypeDetail model class representing a single member of a type ontology (HMFIELD or XSD).
# Used by both the field_types and field_types_info endpoints.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class FieldTypeDetail(Model):

    def __init__(self, type_detail=None, is_mapped: bool=True):
        """
        :param type_detail: delimited type element with elements:
         - mapping_source: either HMFIELD or CEDAR. This only applies for the case of a field mapping--i.e., in
         response to the field_types endpoint, rather than the field_type_info endpoint
         - type_source: either HMFIELD or XSD -- i.e., the type ontology
         - type: term for the type in the type ontology
        :param is_mapped - indicates whether this is used for a field mapping (i.e., the field_types endpoint)

         Examples:
         "HMFIELD|HMFIELD|string"
         "HMFIELD|XSD|xsd:string"
         "CEDAR|XSD|xsd:anyURI"
        """

        self._is_mapped = is_mapped

        # Types for JSON objects
        if self._is_mapped:
            self.openapi_types = {
                'mapping_source': str,
                'type_source': str,
                'type': str
            }
        else:
            self.openapi_types = {
                'type_source': str,
                'type': str
            }

        # Attribute mappings used by the base Model class to assert key/value pairs.
        if self._is_mapped:
            self.attribute_map = {
                'mapping_source': 'mapping_source',
                'type_source': 'type_source',
                'type': 'type'
            }
        else:
            self.attribute_map = {
                'type_source': 'type_source',
                'type': 'type'
            }

        if self._is_mapped:
            self._mapping_source = type_detail.split('|')[0]
            self._type_source = type_detail.split('|')[1]
        else:
            self._type_source = type_detail.split('|')[0]

        # Remove 'xsd:' for XSD type mappings.
        if self._is_mapped:
            type_name = type_detail.split('|')[2]
            if ':' in type_name:
                type_name = type_name.split(':')[1]
        else:
            type_name = type_detail.split('|')[1]
            if ':' in type_name:
                type_name = type_name.split(':')[0]
        self._type = type_name

    def serialize(self):
        # Key/value format of response.
        if self._is_mapped:
            return {
                "mapping_source": self._mapping_source,
                "type_source": self._type_source,
                "type": self._type
            }
        else:
            return {
                "type_source": self._type_source,
                "type": self._type
            }

    @classmethod
    def from_dict(cls, dikt) -> 'FieldTypeDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CelltypeDetailOrgan of this CelltypeDetailOrgan
        :rtype: CelltypeDetailOrgan
        """
        return util.deserialize_model(dikt, cls)

    @property
    def mapping_source(self):
        """Gets the mapping_source of this FieldTypeDetail.
        :return: mapping_source
        :rtype: str
        """
        return self._mapping_source

    @mapping_source.setter
    def mapping_source(self, mapping_source):
        """Sets the mapping_source for the field

        :param mapping_source: The mapping_source of this field
        :type mapping_source: str
        """
        self._mapping_source = mapping_source

    @property
    def type_source(self):
        """Gets the type_source of this FieldTypeDetail.
        :return: type_source
        :rtype: str
        """
        return self._type_source

    @type_source.setter
    def type_source(self, type_source):
        """Sets the type_source for the field

        :param type_source: The type_source of this field
        :type type_source: str
        """
        self._type_source = type_source

    @property
    def type(self):
        """Gets the type of this FieldTypeDetail.
        :return: type
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type for the field

        :param type: The mapping_source of this field
        :param type: str
        """
        self._type = type

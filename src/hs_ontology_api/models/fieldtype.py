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
    def __init__(self, code_ids=None, identifier=None, types=None):
        """
        FieldType - a model defined in OpenAPI

        Represents a code from the HMFIELD ontology.
        :param code_ids: delimited list of code_ids for the metadata field. The code_ids can come from both
                         HMFIELD and CEDAR.
        :param identifier: equivalent of the field key in the yaml (HMFIELD) or field name (CEDAR)
        :param types: delimited list of type mappings for the metadata field.
        Each value in the list has elements:
         - mapping_source: either HMFIELD or CEDAR
         - type_source: either HMFIELD or XSD
         - type

         In general, if a field is common to HMFIELD and CEDAR, the type for the field in HMFIELD will be different
         than its equivalent in CEDAR. In addition, HMFIELDs are mapped to a custom type in HMFIELD and a type in XSD

         For example,
         ["HMFIELD|HMFIELD|string", "HMFIELD|XSD|xsd:string", "CEDAR|XSD|xsd:anyURI"]

        example:
        code_ids - HMFIELD:1008|CEDAR:9f654d25-4de7-4eda-899b-417f05e5d5c3
        identifier - acquisition_instrument_model
        ["HMFIELD|HMFIELD|string", "HMFIELD|XSD|xsd:string", "CEDAR|XSD|xsd:anyURI"]

        The aquisition_instrument_model field is mapped to:
         - the HMFIELD type for string (in HMFIELD)
         - the XSD type for string (in HMFIELD)
         - the XSD type for anyURI in CEDAR

         The anyURI type in CEDAR is used for fields that have valuesets.

        """

        # Types for JSON objects
        self.openapi_types = {
            'code_ids': list[str],
            'identifier': str,
            'types:': list[str]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'code_ids': 'code_ids',
            'identifier': 'identifier',
            'types': 'types'
        }
        # Property assignments
        self._code_ids = code_ids.split('|')
        if identifier is None:
            self._identifier = ''
        else:
            self._identifier = identifier

        dicttype = {}
        listtypes = []

        if types is not None:
            for type in types:
                # Remove 'xsd:' for XSD type mappings.
                type_name = type.split('|')[2]
                if ':' in type_name:
                    type_name = type_name.split(':')[1]
                dicttype = {'mapping_source': type.split('|')[0],
                            'type_source': type.split('|')[1],
                            'type_name' : type_name
                            }
                listtypes.append(dicttype)
        self._types = listtypes

    def serialize(self):
        # Key/value format of response.
        return {
            "code_ids": self._code_ids,
            "identifier": self._identifier,
            "types": self._types
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
    def code_ids(self):
        """Gets the code_ids of this FieldType.
        :return: The code_ids for the field from HMFIELD
        :rtype: str
        """
        return self._code_ids

    @code_ids.setter
    def code_ids(self, code_ids):
        """Sets the code_ids for the field from HMFIELD

        :param code_ids: The code_ids of this field
        :type code_ids: str
        """
        self._code_ids = code_ids

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
    def types(self):
        """Gets the types of this FieldType.
        :return: The types for the field from HMFIELD
        :rtype: dict
        """
        return self._types

    @types.setter
    def types(self, types):
        """Sets the types for the field from HMFIELD

        :param types: The types of this field
        :type types: dict
        """
        self._types = types

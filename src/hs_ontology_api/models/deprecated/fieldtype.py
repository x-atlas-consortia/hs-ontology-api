# coding: utf-8

# JAS December 2023
# FieldType model class
# Used by the field-types endpoint.
# Replicates read of legacy field_types.yaml.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

from hs_ontology_api.models.fieldtype_detail import FieldTypeDetail


class FieldType:
    def __init__(self, code_ids=None, name=None, types=None):
        """
        FieldType - a model defined in OpenAPI

        Represents a code from the HMFIELD ontology.
        :param code_ids: delimited list of code_ids for the metadata field. The code_ids can come from both
                         HMFIELD and CEDAR.
        :param name: equivalent of the field key in the yaml (HMFIELD) or field name (CEDAR)
        :param types: delimited list of type mappings for the metadata field.
        Each value in the list has elements:
         - mapping_source: either HMFIELD or CEDAR
         - type_source: either HMFIELD or XSD
         - type

         In general, if a field is common to HMFIELD and CEDAR, the type for the field in HMFIELD will be different
         from its equivalent in CEDAR. In addition, HMFIELDs are mapped to a custom type in HMFIELD and a type in XSD

         For example,
         ["HMFIELD|HMFIELD|string", "HMFIELD|XSD|xsd:string", "CEDAR|XSD|xsd:anyURI"]

        example:
        code_ids - HMFIELD:1008|CEDAR:9f654d25-4de7-4eda-899b-417f05e5d5c3
        name - acquisition_instrument_model
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
            'name': str,
            'types:': list[str]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'code_ids': 'code_ids',
            'name': 'name',
            'types': 'types'
        }
        # Property assignments
        self._code_ids = code_ids.split('|')
        if name is None:
            self._name = ''
        else:
            self._name = name

        self._types = self._maketypedetail(types=types)

    def _maketypedetail(self, types=None):
        """
        Builds a list of type objects from the delimited list parameter
        :param types: delimited list of type information
        :return: List[dict]
        """

        if types is None:
            return []

        listtypes = []

        for type in types:

            # Instantiate a FieldTypeDetail object.
            fieldtypedetail = FieldTypeDetail(type_detail=type, is_mapped=True)

            # Use the to_dict method of the Model base class to obtain a dict for the list.
            dictfieldtypedetail = fieldtypedetail.to_dict()

            listtypes.append(dictfieldtypedetail)

        return listtypes

    def serialize(self):
        # Key/value format of response.
        return {
            "code_ids": self._code_ids,
            "name": self._name,
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
    def name(self):
        """Gets the name of this FieldType.
        :return: The name for the field
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name for the field from HMFIELD

        :para name: The name of this field
        :type name: str
        """
        self._name = name

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
        :param types: dict
        """
        self._types = types

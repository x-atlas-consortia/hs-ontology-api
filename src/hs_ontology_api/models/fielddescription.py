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
    def __init__(self, code_ids=None, identifier=None, descriptions=None):
        """
        FieldDescription - a model defined in OpenAPI

        Represents associations with metadata fields and assay/datasets.
        Replaces and enhances the legacy field_descriptions.yaml with additional information from
        CEDAR.

        :param code_ids: delimited list of code_ids for the metadata field. The code_ids can come from both
                         HMFIELD and CEDAR.
        :param identifier: equivalent of the field key in the yaml (HMFIELD) or field name (CEDAR)
        :param descriptions: delimited list of descriptions for the metadata field. The descriptions can come from both
                         HMFIELD and CEDAR.
        Each value in the list has elements:
                - source of the description
                - description text

        example:
        code_ids - [HMFIELD:1008|CEDAR:9f654d25-4de7-4eda-899b-417f05e5d5c3]
        field_name - acquisition_instrument_model
        descriptions - [HMFIELD|<description>,CEDAR|<description>]

        """

        # Types for JSON objects
        self.openapi_types = {
            'code_ids': list[str],
            'identifier': str,
            'descriptions:': list[str]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'code_ids': 'code_ids',
            'identifier': 'identifier',
            'descriptions': 'descriptions'
        }
        # Property assignments
        self._code_ids = code_ids.split('|')

        if identifier is None:
            self._identifier = ''
        else:
            self._identifier = identifier

        listdescriptions = []
        if descriptions is not None:
            for description in descriptions:
                dictdescription = {'source': description.split('|')[0],
                             'description': description.split('|')[1]
                                   }
                listdescriptions.append(dictdescription)
        self._descriptions = listdescriptions

    def serialize(self):
        # Key/value format of response.
        return {
            "code_ids": self._code_ids,
            "identifier": self._identifier,
            "descriptions": self._descriptions
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
    def code_ids(self):
        """Gets the code_ids of this FieldDescription.
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
    def descriptions(self):
        """Gets the descriptions of this FieldDescription.
        :return: The descriptions for the field from HMFIELD
        :rtype: str
        """
        return self._descriptions

    @descriptions.setter
    def descriptions(self, descriptions):
        """Sets the descriptions for the field from HMFIELD

        :param descriptions: The description of this field
        :type descriptions: str
        """
        self._descriptions = descriptions
# coding: utf-8

# JAS January 2024
# FieldSchema model class
# Used by the field-schemas endpoint.
# Replicates read of legacy field_schemas.yaml.

from __future__ import absolute_import
# from typing import List
# from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


class FieldSchema:
    def __init__(self, code_ids=None, name=None, schemas=None):
        """
        FieldSchema - a model defined in OpenAPI

        Represents a code from the HMFIELD ontology.
        :param code_ids: delimited list of code_ids for the metadata field. The code_ids can come from both
                         HMFIELD and CEDAR.
        :param name: equivalent of the field key in the yaml (HMFIELD) or field name (CEDAR)
        :param schemas: delimited list of shema mappings for the metadata field.
        Each value in the list has elements:
         - mapping_source: either HMFIELD or CEDAR
         - schema

         In general, if a field is common to HMFIELD and CEDAR, the schema for the field in HMFIELD will be different
         from its equivalent in CEDAR.

         For example,
         ["HMFIELD|sample-section", "HMFIELD|sample-block", "CEDAR|Sample Block", "CEDAR|Sample Section"]

        """

        # Types for JSON objects
        self.openapi_types = {
            'code_ids': list[str],
            'name': str,
            'schemas:': list[str]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'code_ids': 'code_ids',
            'name': 'name',
            'schemas': 'schemas'
        }
        # Property assignments
        self._code_ids = code_ids.split('|')
        if name is None:
            self._name = ''
        else:
            self._name = name

        dictschema = {}
        listschema = []

        if schemas is not None:
            for schema in schemas:
                dictschema = {'source': schema.split('|')[0],
                            'schema': schema.split('|')[1]
                            }
                listschema.append(dictschema)
        self._schemas = listschema

    def serialize(self):
        # Key/value format of response.
        return {
            "code_ids": self._code_ids,
            "name": self._name,
            "schemas": self._schemas
        }

    @classmethod
    def from_dict(cls, dikt) -> 'FieldSchema':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The FieldSchema of this FieldSchema
        :rtype: FieldSchema
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code_ids(self):
        """Gets the code_ids of this FieldSchema.
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
        """Gets the name of this FieldSchema.
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
    def schemas(self):
        """Gets the schemas of this FieldSchema.
        :return: The schemas for the field
        :rtype: dict
        """
        return self._schemas

    @schemas.setter
    def schemas(self, schemas):
        """Sets the schemas for the field from HMFIELD

        :param schemas: The schemas of this field
        :type schemas: dict
        """
        self._schemas = schemas

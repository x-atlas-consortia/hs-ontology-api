# coding: utf-8

# JAS January 2024
# FieldEntity model class
# Used by the field-entities endpoint.
# Replicates read of legacy field_entities.yaml.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

from hs_ontology_api.models.fieldentitydetail import FieldEntityDetail


class FieldEntity(Model):
    def __init__(self, code_ids=None, name=None, entities=None):
        """
        FieldEntity - a model defined in OpenAPI

        Represents a code from the HMFIELD ontology.
        :param code_ids: delimited list of code_ids for the metadata field. The code_ids can come from both
                         HMFIELD and CEDAR.
        :param name: equivalent of the field key in the yaml (HMFIELD) or field name (CEDAR)
        :param entities: delimited list of entity mappings for the metadata field.
        Each entity element in the list has the following format:
        HMFIELD|<Code in HMFIELD>|<term in HMFIELD>;HUBMAP|<Code in HUBMAP>|<term in HUMBMAP>
        i.e.,
           1. The comma delimits the entities associated with a field.
           2. The semicolon delimits the entities by ontology (i.e., HMFIELD or HUBMAP).
           3. The pipe delimits the properties for an entity in an ontology for an entity.
        Example for a field that maps to both the "sample" and "dataset" entities.
        ["HMFIELD|3004|sample;HUBMAP|C040002|Sample", "HMFIELD|3001|dataset;HUBMAP|C040001|Dataset"]
     """

        # Types for JSON objects
        self.openapi_types = {
            'code_ids': list[str],
            'name': str,
            'entities:': list[FieldEntityDetail]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'code_ids': 'code_ids',
            'name': 'name',
            'entities': 'entities'
        }
        # Property assignments
        self._code_ids = code_ids.split('|')
        if name is None:
            self._name = ''
        else:
            self._name = name


        self._entities = self._makeentitydetail(entities=entities)

    def _makeentitydetail(self, entities=None):
        """
        Builds a list of entity detail objects from the delimited list parameter
        :param types: delimited list of type information
        :return: List[dict]
        """

        if entities is None:
            return []

        listentities = []

        for entity in entities:

            # Instantiate a FieldEntityDetail object.
            fieldentitydetail = FieldEntityDetail(entity=entity)

            # Use the to_dict method of the Model base class to obtain a dict for the list.
            dictfieldentitydetail = fieldentitydetail.to_dict()

            listentities.append(dictfieldentitydetail)

        return listentities


    def serialize(self):
        # Key/value format of response.
        return {
            "code_ids": self._code_ids,
            "name": self._name,
            "entities": self._entities
        }

    @classmethod
    def from_dict(cls, dikt) -> 'FieldEntity':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The FieldEntity of this FieldEntity
        :rtype: FieldEntity
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code_ids(self):
        """Gets the code_ids of this FieldEntity.
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
        """Gets the name of this FieldEntity.
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
    def entities(self):
        """Gets the entities of this FieldEntity.
        :return: The entities for the field from HMFIELD
        :rtype: dict
        """
        return self._entities

    @entities.setter
    def entities(self, entities):
        """Sets the entities for the field from HMFIELD

        :param entities: The entities of this field
        :param entities: dict
        """
        self._entities = entities

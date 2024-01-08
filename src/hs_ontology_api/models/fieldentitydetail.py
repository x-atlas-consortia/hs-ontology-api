# coding: utf-8

# JAS January 2024
# FieldEntityDetail model class
# Represents a single HuBMAP provenance entity--e.g., dataset, organ, antibody
# Used by the field-entities endpoint.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


class FieldEntityDetail(Model):
    def __init__(self, entity=None):
        """
        FieldEntityDetail - a model defined in OpenAPI

        Represents a code from the HMFIELD ontology.
        :param entity: delimited list of information for a provenance entity.
        A provenance entity has nodes in both the HMFIELD and HUBMAP ontologies.
        Format of entity string:
        HMFIELD|<Code in HMFIELD>|<term in HMFIELD>;HUBMAP|<Code in HUBMAP>|<term in HUMBMAP>
        i.e.,
           1. The semicolon delimits the entities by ontology (i.e., HMFIELD or HUBMAP).
           2. The pipe delimits the properties for an entity in an ontology for an entity.
        Example for the "dataset" entity:
        ["HMFIELD|3001|dataset;HUBMAP|C040001|Dataset"]
     """

        # Types for JSON objects
        self.openapi_types = {
            'nodes': list[dict]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'nodes': 'nodes',
        }

        # Property assignments
        listnodes = []

        # Split on ontology delimiter.
        nodes = entity.split(';')
        for node in nodes:
            # Split source, code, name
            if '|' in node:
                nodesplit = node.split('|')
                dictnode = {'source': nodesplit[0],
                        'code': nodesplit[1],
                        'name': nodesplit[2]}
                listnodes.append(dictnode)

        self._nodes = listnodes

    def serialize(self):
        # Key/value format of response.
        return {
            "nodes": self._nodes
        }

    @classmethod
    def from_dict(cls, dikt) -> 'FieldEntityDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The FieldEntityDetail of this FieldEntityDetail
        :rtype: FieldEntityDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def nodes(self):
        """Gets the nodes of this FieldEntityDetail.
        :return: nodes
        :rtype: str
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        """Sets the nodes for the entity

        :param code_ids: The nodes of this entity
        :type nodes: str
        """
        self._nodes = nodes

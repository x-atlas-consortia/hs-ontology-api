# coding: utf-8

# JAS November 2023
# CelltypeDetailOrgan model class
# Used by the celltypes endpoint.
# Contains information on an organ associated with a cell type identified in Cell Ontology.

# JAS January 2025
# Added annotation key to the organs object, which describes the annotation used assign organs to cell types.
# Annotations include Azimuth (the original annotation), STELLAR, and DeepCellType

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class CelltypeDetailOrgan(Model):

    def __init__(self, organ=None):
        """

        :param organ: delimited string describing the organ.
        The format of the string is
        <SAB>:<id>|<code>|preferred term|annotation

        """
        # Types for JSON objects
        self.openapi_types = {
            'id': str,
            'source': str,
            'name': str,
            'annotation': str
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'id': 'id',
            'source': 'source',
            'name': 'name',
            'annotation': 'annotation'
        }

        # Property assignments
        if organ is None:
            id = 'unknown'
            source = 'unknown'
            name = 'unknown'
            annotation = 'unknown'
        else:
            organ_info = organ.split('|')
            if len(organ_info) == 1:
                id = organ_info
                source = ''
                name = ''
                annotation = ''
            else:
                source = organ_info[0].split(':')[0]
                id = organ_info[0].split(':')[1]
                name = organ_info[1]
                annotation = organ_info[2]

        self._id = id
        self._source = source
        self._name = name
        self._annotation = annotation

    def serialize(self):
        # Key/value format of response.
        return {
            "id": self._id,
            "source": self._source,
            "name": self._name,
            "annotation": self._annotation
        }

    @classmethod
    def from_dict(cls, dikt) -> 'CelltypeDetailOrgan':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CelltypeDetailOrgan of this CelltypeDetailOrgan
        :rtype: CelltypeDetailOrgan
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """
        Gets the id of this CelltypeDetailOrgan.

        :return: The organ ID
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, reference):
        """
        Sets the id of this CelltypeDetailOrgan.

        :param id: The id for the organ.
        :type id: str
        """
        self._id = id

    @property
    def source(self):
        """
        Gets the source of this CelltypeDetailOrgan.

        :return: The source for the organ
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """
        Sets the source of this CelltypeDetailOrgan.

        :param source: The source for the organ.
        :type source: str
        """
        self._source = source

    @property
    def name(self):
        """
        Gets the name of this CelltypeDetailOrgan.

        :return: The name of the organ
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this CelltypeDetailOrgan
        :param name: The name of the organ.
        :type name: str
        """
        self._name = name

    @property
    def annotation(self):
        """
        Gets the annotation of this CelltypeDetailOrgan.

        :return: The annotation of the organ
        :rtype: str
        """
        return self._annotation

    @annotation.setter
    def annotation(self, annotation):
        """
        Sets the annotation of this CelltypeDetailOrgan
        :param annotation: The name of the organ.
        :type annotation: str
        """
        self._annotation = annotation


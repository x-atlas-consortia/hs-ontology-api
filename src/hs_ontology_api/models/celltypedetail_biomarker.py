# coding: utf-8

# JAS November 2023
# CelltypeDetailBiomarker model class
# Used by the celltypes endpoint.
# Contains information on a biomarker associated with a cell type identified in Cell Ontology.
# Currently, the only biomarker associations are HGNC gene associations from the Human Reference Atlas.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class CelltypeDetailBiomarker(Model):

    def __init__(self, reference=None, biomarker_type=None, entry=None):
        """
        :param reference: Reference for association - currently hard-coded to HRA
        :param biomarker_type: biomarker type - currently hard-coded to "gene"
        :param entry: delimited string of information on a biomarker, in format
        <SAB>:<ID>|preferred term|symbol
        The entry string will be converted to a nested JSON object.
        """

        # Types for JSON objects
        self.openapi_types = {
            'reference': str,
            'biomarker_type': str,
            'entry': dict
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'reference': 'reference',
            'biomarker_type': 'biomarker_type',
            'entry': 'entry'
        }
        # Property assignments
        if reference is None:
            self._reference = 'unknown'
        else:
            self._reference = reference
        if biomarker_type is None:
            self._biomarker_type = 'unknown'
        else:
            self._biomarker_type = biomarker_type

        if entry is None:
            self._entry = {}
        else:
            # Parse biomarker details from the delimited string.
            entry_info = entry.split('|')
            if len(entry_info) == 1:
                vocabulary = entry_info
                id = ''
                name = ''
                symbol = ''
            else:
                # Parse and map.
                # <vocabulary>:id|name|symbol
                vocabulary = entry_info[0].split(':')[0]
                id = entry_info[0].split(':')[1]
                name = entry_info[1]
                symbol = entry_info[2]
            dictentry = {'vocabulary': vocabulary,
                         'id': id,
                         'name': name,
                         'symbol': symbol}
            self._entry= dictentry

    def serialize(self):
        # Key/value format of response.
        return {
            "reference": self._reference,
            "biomarker_type": self._biomarker_type,
            "entry": self._entry
        }

    @classmethod
    def from_dict(cls, dikt) -> 'CelltypeDetailBiomarker':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CelltypeDetailBiomarker of this CelltypeDetailBiomarker
        :rtype: CelltypeDetailBiomarkers
        """
        return util.deserialize_model(dikt, cls)

    @property
    def reference(self):
        """
        Gets the reference of this CelltypeDetailBiomarker.

        :return: The reference for the biomarker's association
        :rtype: str
        """
        return self._reference

    @reference.setter
    def reference(self, reference):
        """
        Sets the reference of this CelltypeDetailBiomarker.

        :param reference: The reference for the biomarker's association.
        :type reference: str
        """
        self._reference = reference

    @property
    def biomarker_type(self):
        """
        Gets the biomarker_type of this CelltypeDetailBiomarker.

        :return: The biomarker type for the biomarker
        :rtype: str
        """
        return self._biomarker_type

    @biomarker_type.setter
    def biomarker_type(self, biomarker_type):
        """
        Sets the biomarker_type of this CelltypeDetailBiomarker.

        :param biomarker_type: The biomarker_type for the biomarker.
        :type biomarker_type: str
        """
        self._biomarker_type = biomarker_type

    @property
    def entry(self):
        """
        Gets the entry of this CelltypeDetailBiomarker.

        :return: The entry object for the biomarker
        :rtype: str
        """
        return self._entry

    @entry.setter
    def entry(self, entry):
        """
        Sets the entry of this CelltypeDetailBiomarker
        :param entry: The entry object for the biomarker.
        :type entry: str
        """
        self._entry = entry
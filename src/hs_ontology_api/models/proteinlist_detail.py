# coding: utf-8

# JAS November 2023
# ProteinsListDetail model class
# Used by the proteins-info endpoint.
# Provides information on proteins identified by either the UBKG or the Cells API--i.e., that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class ProteinListDetail(Model):
    def __init__(self, uniprotkb_id=None, recommended_name=None, entry_name=None, synonyms=None):
        """ProteinListDetail - a model defined in OpenAPI

            :param uniprotkb_id: UniProtKB identifier for protein
            :type uniprotkb_id: str
            :param recommended_name: UniProtKB recommended name
            :type recommended_name: str
            :param entry_name: UniProtKB entry name
            :type entry_name: str
            :param synonyms: other synonyms
            :type synonyms: List[str]

        """
        # Types for JSON objects
        self.openapi_types = {
            'uniprotkb_id': str,
            'recommended_name': str,
            'entry_name': str,
            'synonyms':List[str]
        }

        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'uniprotkb_id': 'uniprotkb_id',
            'recommended_name': 'recommended_name',
            'entry_name': 'entry_name',
            'synonyms': 'synonyms'
        }

        # Property assignments
        self._uniprotkb_id = uniprotkb_id
        if recommended_name is None:
            self._recommended_name = ''
        else:
            self._recommended_name = recommended_name[0]

        if entry_name is None:
            self._entry_name = ''
        else:
            self._entry_name = entry_name[0]

        if synonyms is None:
            self._synonyms = []
        else:
            self._synonyms = synonyms


    def serialize(self):
        # Key/value format of response.
        return {
            "uniprotkb_id": self._uniprotkb_id,
            "recommended_name": self._recommended_name,
            "entry_name": self._entry_name,
            "synonyms": self._synonyms
        }

    @classmethod
    def from_dict(cls, dikt) -> 'ProteinListDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetail of this GenesFromCells
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def uniprotkb_id(self):
        """Gets the uniprotkb_id of this ProtienListDetail.

        uniprotkb_id for the protein.
        :return: The uniprotkb_id of this ProteinListDetail.
        :rtype: str
        """
        return self._uniprotkb_id

    @uniprotkb_id.setter
    def uniprotkb_id(self, uniprotkb_id):
        """Sets the uniprotkb_id of this ProteinListDetail.

        :param uniprotkb_id: The uniprotkb_id of this protein
        :type uniprotkb_id: str
        """

        self._uniprotkb_id = uniprotkb_id

    @property
    def recommended_name(self):
        """Gets the recommended_name of this ProteinListDetail.

        Current recommended_name for the protein.
        :return: The recommended_name of this ProteinListDetail.
        :rtype: str
        """
        return self._recommended_name

    @recommended_name.setter
    def recommended_name(self, recommended_name):
        """Sets the recommended_name of this ProteinListDetail.


        :param recommended_name: The recommended_name of this ProteinListDetail
        :type recommended_name: str
        """

        self._recommended_name = recommended_name

    @property
    def entry_name(self):
        """Gets the entry_name of this ProteinListDetail.

        :return: The entry_name of this ProteinListDetail.
        :rtype: str
        """
        return self._entry_name

    @entry_name.setter
    def entry_name(self, entry_name):
        """Sets the entry_name of this ProteinListDetail.

        :param entry_name: The entry_name of this ProteinListDetail
        :type entry_name: str
        """

        self._entry_name = entry_name

    @property
    def synonyms(self):
        """Gets the synonyms list of this ProteinListDetail.

        :return: The synonyms of this ProteinListDetail.
        :rtype: str
        """
        return self._synonyms

    @synonyms.setter
    def synonyms(self, synonyms):
        """Sets the synonyms of this ProteinListDetail.

        :param synonyms: The entry_name of this ProteinListDetail
        :type synonyms: str
        """

        self._synonyms = synonyms

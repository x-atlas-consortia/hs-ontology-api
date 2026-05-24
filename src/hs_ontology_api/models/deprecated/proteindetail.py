# coding: utf-8

# JAS November 2023
# ProteinDetail model class
# Used by the proteins endpoint.
# Contains information on a protein identified in UniProtKB.
from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


# NOV 2023
# The UNIPROTKB ETL currently does not correctly parse synonyms that include nested parentheses, so the
# object will not return synonym information.

class ProteinDetail(Model):
    def __init__(self, uniprotkb_id=None, recommended_name=None, entry_name=None, synonyms=None, description=None):
        """
        ProteinDetail - a model defined in OpenAPI
        :param self: 
        :param uniprotkb_id: UniprotKB ID for protein
        :param recommended_name: UniProtKB recommended name
        :param entry_name: UniProtKB entry name
        :param synonyms: UniProtKB synonyms
        :return: dict
        """
        # Types for JSON objects
        self.openapi_types = {
            'uniprotkb_id': str,
            'recommended_name': str,
            'entry_name': str,
            #'synonyms': List[str],
            'references': List[str] #List[ProteinDetailReference]
        }
        # Attributes
        self.attribute_map = {
            'uniprotkb_id': 'uniprotkb_id',
            'recommended_name': 'recommended_name',
            'entry_name': 'entry_name',
            #'synonyms': 'synonyms',
            'references': 'references'
        }
        # Property assignments
        self._uniprotkb_id = uniprotkb_id
        if recommended_name is None:
            self._recommended_name = ''
        else:
            self._recommended_name = recommended_name
        if entry_name is None:
            self._entry_name = ''
        else:
            self._entry_name = entry_name
        #if synonyms is None:
            #self._synonyms = []
        #else:
            #self._synonyms = synonyms

        if description is None:
            desc = ''
        else:
            desc = description[0]

        self._references = [
            {'source':'uniprotkb',
             'entry': desc,
             'url': f'https://www.uniprot.org/uniprotkb/{self._uniprotkb_id}/entry',
             'curation':'swissprot',
             'organism':['Homo sapiens']
             }]

    def serialize(self):
        # Key/value format of response.
        return {
            "uniprotkb_id": self._uniprotkb_id,
            "recommended_name": self._recommended_name,
            "entry_name": self._entry_name,
            #"synonyms": self._synonyms,
            "references": self._references
            }

    @classmethod
    def from_dict(cls, dikt) -> 'ProteinDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ProteinDetail of this ProteinDetail
        :rtype: ProteinDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def uniprotkb_id(self):
        """Gets the uniprotkb_id of this ProteinDetail.

        uniprotkb_id for the protein.
        :return: The uniprotkb_id of this ProteinDetail.
        :rtype: str
        """
        return self._uniprotkb_id

    @uniprotkb_id.setter
    def uniprotkb_id(self, uniprotkb_id):
        """Sets the uniprotkb_id of this ProteinDetail.

        :param uniprotkb_id: The uniprotkb_id of this protein
        :type uniprotkb_id: str
        """

        self._uniprotkb_id = uniprotkb_id

    @property
    def recommended_name(self):
        """Gets the recommended_name of this ProteinDetail.

        Current recommended_name for the protein.
        :return: The recommended_name of this ProteinDetail.
        :rtype: str
        """
        return self._recommended_name

    @recommended_name.setter
    def recommended_name(self, recommended_name):
        """Sets the recommended_name of this ProteinDetail.

        :param recommended_name: The recommended_name of this ProteinDetail
        :type recommended_name: str
        """

        self._recommended_name = recommended_name

    @property
    def entry_name(self):
        """Gets the entry_name of this ProteinDetail.

        :return: The entry_name of this ProteinDetail.
        :rtype: str
        """
        return self._entry_name

    @entry_name.setter
    def entry_name(self, entry_name):
        """Sets the entry_name of this ProteinDetail.

        :param entry_name: The entry_name of this ProteinDetail
        :type entry_name: str
        """

        self._entry_name = entry_name

    #@property
    #def synonyms(self):
        """Gets the synonyms list of this ProteinDetail.

        :return: The synonyms of this ProteinDetail.
        :rtype: str
        """
        #return self._synonyms

    #@synonyms.setter
    #def synonyms(self, synonyms):
        """Sets the synonyms of this ProteinDetail.

        :param synonyms: The entry_name of this ProteinDetail
        :type synonyms: str
        """
        #self._synonyms = synonyms

    @property
    def references(self):
        """Gets the references list of this ProteinDetail.

        :return: The references of this ProteinDetail.
        :rtype: str
        """
        return self._references

    @references.setter
    def references(self, references):
        """Sets the references of this ProteinDetail.

        :param references: The references of this ProteinDetail
        :type synonyms: str
        """
        self._references = references


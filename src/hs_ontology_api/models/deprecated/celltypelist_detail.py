# coding: utf-8

# JAS November 2023
# CelltypesListDetail model class
# Used by the celltypes-info endpoint.
# Provides information on cell types identified by either the UBKG or the Cells API--i.e.,
# that have relevance to HuBMAP/SenNet.

from __future__ import absolute_import
# from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


class CelltypesListDetail(Model):
    def __init__(self, id=None, term=None, synonyms=None, definition=None):
        """CelltypesListDetail - a model defined in OpenAPI

            :param id: Cell Ontology ID
            :type id: str
            :param term: preferred term from CL
            :type term: str
            :param synonyms: synonyms from CL
            :type approved_name: List[str]
            :param definition:  description
            :type definition: str

        """
        # Types for JSON objects
        self.openapi_types = {
            'id': str,
            'term': str,
            'synonyms': list[str],
            'definition': str
        }

        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'id': 'id',
            'term': 'term',
            'synonyms': 'synonyms',
            'definition': 'definition'
        }

        # Property assignments
        self._id = id
        if term is None:
            self._term = ''
        else:
            self._term = term

        if synonyms is None:
            self._synonyms = []
        else:
            self._synonyms = synonyms

        if definition is None:
            self._definition = ''
        else:
            self._definition= definition

    def serialize(self):
        # Key/value format of response.
        return {
            "id": self._id,
            "term": self._term,
            "synonyms": self._synonyms,
            "definition": self._definition,
        }

    @classmethod
    def from_dict(cls, dikt) -> 'CelltypesListDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CelltypeListDetail of this CelltypesListDetail
        :rtype: CelltypesListDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this CelltypesListDetail.

        CL ID
        :return: The id of this GeneListDetail.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this CelltypesListDetail.

        CL ID for the cell type

        :param hgnc_id: The hgnc_id of this gene
        """

        self._id = id

    @property
    def term(self):
        """Gets the term of this CelltypesListDetail.

        Current term for the cell type
        :return: The term of this CelltypesListDetail.
        :rtype: str
        """
        return self._term

    @term.setter
    def term(self, term):
        """Sets the term of this CelltypesListDetail.

        Current CL term for the cell type

        :param term: The approved term for this cell type
        :type term: str
        """

        self._term= term

    @property
    def synonyms(self):
        """Gets the synonyms of this CelltypesListDetail.

        synonyms for the cell type
        :return: The synonyms of this CelltypesListDetail.
        :rtype: List[str]
        """
        return self._synonyms

    @synonyms.setter
    def synonyms(self, synonymz):
        """Sets the synonyms of this CelltypesListDetail.

        Current synonyms for the cell type
        :param synonyms: The synonyms of this cell type
        :type synonyms: List[str]
        """

        self._synonyms = synonyms

    @property
    def definition(self):
        """Gets the definition of this CelltypesListDetail.

        definition
        :return: The definition of this CelltypesListDetail.
        :rtype: str
        """
        return self._definition

    @definition.setter
    def definition(self, definition):
        """Sets the definition of this CelltypesListDetail.

       defintion

        :param definition: The defintion of this cell type
        :type summary: str
        """

        self._defintion = definition

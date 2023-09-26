# coding: utf-8

# JAS September 2023
# GeneDetailReference model
# Information on a reference for a gene identified in HGNC.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class GeneDetailReference(Model):
    def __init__(self, code=None, type=None, url=None):
        """GeneDetailReference - a model defined in OpenAPI
                :param code: a reference code for a gene
                :type code: str
                :param type: the type of reference for a gene
                :type type: str
                :param url: the url for the reference in the reference vocabulary
                :type url: str
        """
        # The code argument is a code to which a gene with a particular HGNC ID corresponds.
        # Reference codes are either synonyms from other vocabularies (e.g. Entrez) or from relationships
        # (e.g., gene-protein mappings from UniProtKB).

        self.openapi_types = {
            'code': str,
            'type': str,
            'url': str
        }
        self.attribute_map = {
            'code': 'code',
            'type': 'type',
            'url': 'url'
        }
        self._code = code

        sab = code.split(':')[0].lower()
        if sab == 'hgnc':
            sab = 'hugo'
        id = code.split(':')[1]

        # Expand reference.
        self._type = sab

        # Map to vocabulary-specific references

        match sab:
            case 'entrez':
                url = f'https://www.ncbi.nlm.nih.gov/gene/{id}'
            case 'uniprotkb':
                url = f'https://www.uniprot.org/uniprotkb/{id}/entry'
            case 'ensembl':
                url = f'http://useast.ensembl.org/Homo_sapiens/Gene/Summary?g={id}'
            case 'omim':
                url = f'https://www.omim.org/entry/601456?search={id}'
            case 'hugo':
                url =f'https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{code}'
            case _:
                url = ''
        self._url = url

    def serialize(self):
        # Key/value formatting for response.
        return {
            "code": self._code,
            "type": self._type,
            "url": self._url

        }

    @classmethod
    def from_dict(cls, dikt) -> 'GeneDetailReference':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetailReference of this GeneDetailReference
        :rtype: GeneDetailReference
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code(self):
        """Gets the code of this GeneDetailReference.

        Code for the reference
        :return: code for the reference
        :rtype: str
        """
        return self._code

    @code.setter
    def reference_code(self, code):
        """Sets the code of this GeneDetailReference.

        Code for the reference

        :param code: The reference code
        :type code: str
        """

        self._code = code

    @property
    def type(self):
        """Gets the type for this GeneDetailReference.

        Type of reference.
        :return: The type of this GeneDetailReference.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this GeneDetailReference.

        reference type

        :param type: The reference_type of this GeneDetailReference
        :type type: str
        """

        self._type = type

    @property
    def url(self):
        """Gets the url of this GeneDetailReference.

        URL to the vocabulary for the reference.
        :return: The url of this GeneDetailReference.
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this GeneDetailReference.

        URL for the reference

        :param url: The refernence_url of this GeneDetailReference
        :type url: str
        """

        self._url= url

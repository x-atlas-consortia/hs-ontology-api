# coding: utf-8

# JAS September 2023
# GeneDetailReference model
# Information on a reference for a gene identified in HGNC.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class GeneDetailReference(Model):
    def __init__(self, code=None, source=None, url=None):
        """GeneDetailReference - a model defined in OpenAPI
                :param code: a reference code for a gene, in format SAB:CODE
                :type code: str
                :param source: the vocabulary (SAB) for the reference for a gene
                :type type: str
                :param url: the url for the reference in the reference vocabulary
                :type url: str
        """
        # The code argument is a code to which a gene with a particular HGNC ID corresponds.
        # Reference codes are either synonyms from other vocabularies (e.g. Entrez) or from relationships
        # (e.g., gene-protein mappings from UniProtKB).

        self.openapi_types = {
            'id': str,
            'source': str,
            'url': str
        }
        self.attribute_map = {
            'id': 'id',
            'source': 'source',
            'url': 'url'
        }
        self._id = code.split(':')[1]

        self._source = code.split(':')[0].lower()
        if self._source == 'hgnc':
            self._source = 'hugo'

        # Map to vocabulary-specific references

        if self._source == 'entrez':
            url = f'https://www.ncbi.nlm.nih.gov/gene/{self._id}'
        elif self._source == 'uniprotkb':
            url = f'https://www.uniprot.org/uniprotkb/{self._id}/entry'
        elif self._source == 'ensembl':
            url = f'http://useast.ensembl.org/Homo_sapiens/Gene/Summary?g={self._id}'
        elif self._source == 'omim':
            url = f'https://www.omim.org/entry/601456?search={self._id}'
        elif self._source in ['hugo','hgnc']:
            url =f'https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/{code}'
        else:
            url = ''
        self._url = url

    def serialize(self):
        # Key/value formatting for response.
        return {
            "id": self._id,
            "source": self._source,
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
    def id(self):
        """Gets the id of this GeneDetailReference.

        ID for the reference
        :return: id for the reference
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the code of this GeneDetailReference.

        Code for the reference

        :param id: The reference code
        :type id: str
        """

        self._id = id

    @property
    def source(self):
        """Gets the source for this GeneDetailReference.

        Source of reference.
        :return: The source of this GeneDetailReference.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this GeneDetailReference.

        reference source

        :param source: The source of this GeneDetailReference
        :type source: str
        """

        self._source = source

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

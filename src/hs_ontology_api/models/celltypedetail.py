# coding: utf-8

# JAS November 2023
# CelltypeDetail model class
# Used by the celltypes endpoint.
# Contains information on a cell type identified in Cell Ontology.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


class CelltypeDetail(Model):
    def __init__(self, cl_id=None, name=None, definition=None, biomarkers=None,organs=None):
        """
        CelltypeDetail: a model in OpenAPI

        :param cl_id: Cell Ontology ID for the cell type
        :param name: Preferred term for the cell type
        :param definition: Definition for the cell type
        :param biomarkers: array of information on the biomarkers associated with the cell type
        based on the HRA ontology.
        :param organs: array of Cell Ontology:Azimuth:UBERON organ mappings
        The biomarkers and organs arrays will be used to build a nested object.


        As of November 2023, the only biomarker-cell type associations in HRA are for genes.
        """

        # Types for JSON objects
        self.openapi_types = {
            'cl_id': str,
            'name': List[str],
            'definition': List[str],
            'biomarkers': List[dict],
            'organs':List[dict]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'cl_id': 'cl_id',
            'name': 'name',
            'definition': 'definition',
            'biomarkers': 'biomarkers',
            'organs': 'organs'
        }
        # Property assignments
        self._cl_id = cl_id
        if name is None:
            self._name = ''
        else:
            self._name = name[0]
        if definition is None:
            self._definition = ''
        else:
            self._definition = definition[0]

        if biomarkers is None:
            self._biomarkers = []
        else:
            listbiomarkers = []
            # Currently, the only biomarker type is gene.
            for biomarker in biomarkers:
                # Each array element describes a gene from HGNC in format
                # HGNC:ID |approved name | approved symbol
                dictbiomarker = {'reference': 'Human Reference Atlas',
                                 'biomarker_type': 'gene'}
                geneinfo = biomarker.split('|')
                dictgene = {'vocabulary': 'HGNC',
                            'id': geneinfo[0].split(':')[1],
                            'name': geneinfo[1],
                            'symbol': geneinfo[2]}
                dictbiomarker['entry'] = dictgene
                listbiomarkers.append(dictbiomarker)

            self._biomarkers = listbiomarkers

    def serialize(self):
        # Key/value format of response.
        return {
            "cl_id": self._cl_id,
            "name": self._name,
            "definition": self._definition,
            "biomarkers": self._biomarkers,

        }

    @classmethod
    def from_dict(cls, dikt) -> 'CelltypeDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetail of this GeneDetail
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def cl_id(self):
        """Gets the cl_id of this CelltypeDetail.

        Cell Ontology ID for this cell type.
        :return: The Cell Ontology ID of this GeneDetail.
        :rtype: str
        """
        return self._cl_id

    @cl_id.setter
    def cl_id(self, cl_id):
        """Sets the Cell Ontology ID of this CelltypeDetail.

         Cell Ontology ID for this cell type.
        :param cl_id: The cl_id of this CelltypeDetail
        :type cl_id: str
        """

        self._cl_id = cl_id

    @property
    def name(self):
        """Gets the name of this CelltypeDetail.

        Cell Ontology preferred term for this cell type.
        :return: The name of this GeneDetail.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the Cell Ontology name of this CelltypeDetail.

         Cell Ontology name for this cell type.
        :param name: The name of this CelltypeDetail
        :type name: str
        """

        self._name = name

    @property
    def definition(self):
        """Gets the definition of this CelltypeDetail.

        Cell Ontology definition for this cell type.
        :return: The name of this GeneDetail.
        :rtype: str
        """
        return self._name

    @definition.setter
    def definition(self, definition):
        """Sets the Cell Ontology definition of this CelltypeDetail.

         Cell Ontology definition for this cell type.
        :param definition: The definition of this CelltypeDetail
        :type definition: str
        """

        self._definition = definition

    @property
    def biomarkers(self):
        """Gets the biomarkers array of this CelltypeDetail.

        HRA biomarker associations for this cell type.
        :return: The biomarkers of this GeneDetail.
        :rtype: List[dict]
        """
        return self._biomarkers

    @biomarkers.setter
    def biomarkers(self, biomarkers):
        """Sets the biomarkers of this CelltypeDetail.

          HRA biomarker associations for this cell type.
        :param biomarkers: The biomarkers array of this CelltypeDetail
        :type biomarkers: List[dict]
        """

        self._biomarkers = biomarkers

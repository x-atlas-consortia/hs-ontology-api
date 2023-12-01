# coding: utf-8

# JAS November 2023
# CelltypeDetail model class
# Used by the celltypes endpoint.
# Contains information on a cell type identified in Cell Ontology.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

# Sub-object models
# Array of biomarkers objects
from hs_ontology_api.models.celltypedetail_biomarker import CelltypeDetailBiomarker
from hs_ontology_api.models.celltypedetail_organ import CelltypeDetailOrgan


class CelltypeDetail(Model):
    def __init__(self, cl_id=None, name=None, definition=None, biomarkers=None, organs=None):
        """
        CelltypeDetail: a model in OpenAPI

        :param cl_id: Cell Ontology ID for the cell type
        :param name: Preferred term for the cell type
        :param definition: Definition for the cell type
        :param biomarkers: array of information on the biomarkers associated with the cell type
        based on the HRA ontology.
        :param organs: array of Cell Ontology:Azimuth:UBERON organ mappings

        The cl_id, name, and definition will be used to build a nested object.
        The biomarkers and organs arrays will be used to build arrays of nested objects.

        As of November 2023, the only biomarker-cell type associations in HRA are for genes.
        """

        # Types for JSON objects
        self.openapi_types = {
            'celltype': dict,
            'biomarkers': List[CelltypeDetailBiomarker],
            'organs': List[CelltypeDetailOrgan]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'celltype': 'celltype',
            'biomarkers': 'biomarkers',
            'organs': 'organs'
        }
        # Property assignments
        dict_cell_type = {'cl_id': cl_id}
        if name is None:
            dict_cell_type['name'] = ''
        else:
            dict_cell_type['name'] = name[0]
        if definition is None:
            dict_cell_type['definition'] = ''
        else:
            dict_cell_type['definition'] = definition[0]
        self._cell_type = dict_cell_type

        # Biomarkers object
        if biomarkers is None:
            self._biomarkers = []
        else:
            self._biomarkers = self._makebiomarkersdict(biomarkers=biomarkers)

        # Organs object
        if organs is None:
            self._organs = []
        else:
            self._organs = self._makeorganssdict(organs=organs)

    def _makebiomarkersdict(self, biomarkers=None):

        """
        Builds a list of dictionaries of biomarkers associated with a cell type.
        :param biomarkers: optional list of biomarkers associated with a cell type.
        Each array element describes a biomarker in format
        SAB:ID |approved name| approved symbol
        :return: dict
        """

        if biomarkers is None:
            return []

        listbiomarkers = []
        for biomarker in biomarkers:
            # Currently, the only biomarker associations are from HRA for genes.
            # Instantiate a biomarker object.
            celltypedetailbiomarker = CelltypeDetailBiomarker(reference='Human Reference Atlas', biomarker_type='gene',
                                                              entry=biomarker)
            # Use the to_dict method of the Model base class to obtain a dict for the list.
            dictcelltypebiomarker = celltypedetailbiomarker.to_dict()

            listbiomarkers.append(dictcelltypebiomarker)

        return listbiomarkers

    def _makeorganssdict(self, organs=None):

        """
        Builds a list of dictionaries of organs associated with a cell type.
        :param organs: optional list of organs associated with a cell type.
        Each array element describes a biomarker in format
        [<SAB>:<ID>|name,<SAB2>:<ID2|name2...]
        :return: dict
        """
        if organs is None:
            return []

        # The query returns the delimited string as a list.
        organsplit = organs[0].split(',')

        listorgans = []

        for organ in organsplit:

            # Instantiate a organ object.
            celltypedetailorgan = CelltypeDetailOrgan(organ=organ)
            # Use the to_dict method of the Model base class to obtain a dict for the list.
            dictcelltypedetailorgan = celltypedetailorgan.to_dict()

            listorgans.append(dictcelltypedetailorgan)

        return listorgans

    def serialize(self):
        # Key/value format of response.
        return {
            "cell_type": self._cell_type,
            "biomarkers": self._biomarkers,
            "organs": self._organs
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
    def cell_type(self):
        """Gets the cell_type object of this CelltypeDetail.
        :return: The cell_type object of this CelltypeDetail.
        :rtype: str
        """
        return self._cell_type

    @cell_type.setter
    def cell_type(self, cell_type):
        """Sets the identifier object of this CelltypeDetail.

         Identifier object for this cell type.
        :param cell_type: The cell_type of this CelltypeDetail
        :type cell_type: dict
        """

        self._cell_type = cell_type

    @property
    def biomarkers(self):
        """Gets the biomarkers array of this CelltypeDetail.

        HRA biomarker associations for this cell type.
        :return: The biomarkers of this CelltypeDetail.
        :rtype: List[CelltypeDetailBiomarker]
        """
        return self._biomarkers

    @biomarkers.setter
    def biomarkers(self, biomarkers):
        """Sets the biomarkers of this CelltypeDetail.

          HRA biomarker associations for this cell type.
        :param biomarkers: The biomarkers array of this CelltypeDetail
        :type biomarkers: List[CelltypeDetailBiomarker]
        """

        self._biomarkers = biomarkers

    @property
    def organs(self):
        """Gets the organs array of this CelltypeDetail.

        :return: The organs array of this GeneDetail.
        :rtype: List[CelltypeDetailOrgan]
        """
        return self._organs

    @organs.setter
    def organs(self, organs):
        """Sets the organs array of this CelltypeDetail.


        :param organs: The organs array of this CelltypeDetail
        :type organs: List[CelltypeDetailOrgan]
        """

        self._organs = organs

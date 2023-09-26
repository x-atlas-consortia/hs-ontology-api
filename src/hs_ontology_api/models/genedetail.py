# coding: utf-8

# JAS September 2023
# GeneDetail model
# Information on a gene identified in HGNC.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

from hs_ontology_api.models.genedetail_reference import GeneDetailReference
from hs_ontology_api.models.genedetail_celltype import GeneDetailCellType

class GeneDetail(Model):
    def __init__(self, hgnc_id=None, approved_symbol=None, approved_name=None, previous_symbols=None,
                 previous_names=None, alias_symbols=None, alias_names=None, references=None,
                 summaries=None, cell_types_code=None, cell_types_code_name=None):
        """GeneDetail - a model defined in OpenAPI

                :param hgnc_id: HGNC id approved id for the gene
                :type hgnc_id: str
                :param approved_symbol: HGNC current approved symbol for the gene
                :type approved_symbol: str
                :param approved_name: HGNC current approved name for the gene
                :type approved_name: str
                :param previous_symbols: list of HGNC previous symbols for the gene
                :type approved_name: List[str]
                :param previous_names: list of HGNC previous names for the gene
                :type previous_names: List[str]
                :param alias_symbols: list of HGNC alias symbols for the gene
                :type alias_symbols: List[str]
                :param alias_names: list of HGNC alias names for the gene
                :type alias_names: List[str]
                :param references: list of references for the gene
                :type references: List[GeneDetailReference]
                :param summaries: RefSeq summary for the gene
                :type summaries: List[str]
                :param cell_types: list of cell types for the gene
                :type cell_types: List[GeneDetailCellType]
                :param cell_types_code_name: list of names for cell types for the gene
                :type cell_types_code_name: List[str]

        """
        # cell_types_code_name is used to build nested objects in cell_types.

        # Types for JSON objects
        self.openapi_types = {
            'hgnc_id': str,
            'approved_symbol': str,
            'approved_name': str,
            'previous_symbols': List[str],
            'previous_names': List[str],
            'alias_symbols': List[str],
            'alias_names': List[str],
            'references': List[GeneDetailReference],
            'summaries': List[str],
            'cell_types_code': List[GeneDetailCellType]
        }

        self.attribute_map = {
            'hgnc_id': 'hgnc_id',
            'approved_symbol': 'approved_symbol',
            'approved_name': 'approved_name',
            'previous_symbols': 'previous_symbols',
            'previous_names': 'previous_names',
            'alias_symbols': 'alias_symbols',
            'alias_names': 'alias_names',
            'references': 'references',
            'summaries': 'summaries',
            'cell_types_code': 'cell_types_code'
        }
        self._hgnc_id = hgnc_id
        self._approved_symbol = approved_symbol
        self._approved_name = approved_name
        self._previous_symbols = previous_symbols
        self._previous_names = previous_names
        self._alias_symbols = alias_symbols
        self._alias_names = alias_names
        self._references = self.makereferencedict(references)
        self._summaries = summaries
        self._cell_types_code = self.makecelltypedict(cell_types_code,cell_types_code_name)

    def makereferencedict(self, references=None) ->List[dict]:

        # Expands a list of reference codes into dictionaries with additional properties.

        # Each reference code will be expanded to a JSON object with additional key/value pairs, including for
        # a URL.
        listret=[]
        if references is None:
            return None

        for ref in references:
            genedetailref = GeneDetailReference(ref)
            # Use the to_dict method of the Model base class to obtain a dict of genedetailref.
            dictref = genedetailref.to_dict()
            listret.append(dictref)

        return listret

    def makecelltypedict(self, cell_types_code=None, cell_types_code_name=None) ->List[dict]:

        # Expands a list of cell_type codes into dictionaries with additional properties.

        # Each reference code will be expanded to a JSON object with additional key/value pairs, including for
        # a URL.
        listret=[]
        if cell_types_code is None:
            return None

        for cell in cell_types_code:

            # Look for matching name for the cell type in cell_types_code_name.
            # The elements in cell_types_code_name are in format CL:CODE|name
            if cell_types_code_name is not None:
                name = ''
                for nam in cell_types_code_name:
                    cl_code = nam.split('|')[0]
                    if cl_code == cell:
                        name = nam.split('|')[1]
                        break

            genedetailcelltype = GeneDetailCellType(cell,name)
            # Use the to_dict method of the Model base class to obtain a dict of genedetailref.
            dictcell = genedetailcelltype.to_dict()
            listret.append(dictcell)

        return listret

    def serialize(self):
        # Key/value format of response.
        return {
            "hgnc_id": self._hgnc_id,
            "approved_symbol": self._approved_symbol,
            "approved_name": self._approved_name,
            "previous_symbols": self._previous_symbols,
            "previous_names": self._previous_names,
            "alias_symbols": self._alias_symbols,
            "alias_names": self._alias_names,
            "references": self._references,
            "summary": self._summaries,
            "cell_types": self._cell_types_code
        }

    @classmethod
    def from_dict(cls, dikt) -> 'GeneDetail':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetail of this GeneDetail
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    @property
    def hgnc_id(self):
        """Gets the hgnc_id of this GeneDetail.

        Current HGNC approved id for the gene.
        :return: The hgnc_id of this GeneDetail.
        :rtype: str
        """
        return self._hgnc_id

    @hgnc_id.setter
    def hgnc_id(self, hgnc_id):
        """Sets the approved_symbol of this GeneDetail.

        Current HGNC approved id for the gene.

        :param approved_id: The approved_id of this GeneInfo
        :type approved_id: str
        """

        self._hgnc_id = hgnc_id

    @property
    def approved_symbol(self):
        """Gets the approved_symbol of this GeneDetail.

        Current HGNC approved symbol for the gene.
        :return: The approved_symbol of this GeneDetail.
        :rtype: str
        """
        return self._approved_symbol

    @approved_symbol.setter
    def approved_symbol(self, approved_symbol):
        """Sets the approved_symbol of this GeneDetail.

        Current HGNC approved symbol for the gene.

        :param approved_symbol: The approved_symbol of this GeneInfo
        :type approved_symbol: str
        """

        self._approved_symbol = approved_symbol

    @property
    def previous_symbols(self):
        """Gets the previous_names of this GeneDetail.

        Current HGNC previous symbols for the gene.
        :return: The previous_symbols of this GeneDetail.
        :rtype: str
        """
        return self._previous_symbols

    @previous_symbols.setter
    def previous_symbols(self, previous_symbols):
        """Sets the previous_symbols of this GeneDetail.

        Current HGNC previous_symbols for the gene.

        :param previous_symbols: The previous_symbols of this GeneInfo
        :type previous_symbols: str
        """

        self._previous_symbols = previous_symbols

    @property
    def previous_names(self):
        """Gets the previous_names of this GeneDetail.

        Current HGNC previous names for the gene.
        :return: The previous_names of this GeneDetail.
        :rtype: str
        """
        return self._previous_names

    @previous_names.setter
    def previous_names(self, previous_names):
        """Sets the previous_names of this GeneDetail.

        Current HGNC previous_names for the gene.

        :param previous_names: The previous_names of this GeneInfo
        :type previous_names: str
        """

        self._previous_names = previous_names

    @property
    def alias_symbols(self):
        """Gets the alias_symbols of this GeneDetail.

        Current HGNC alias_symbols for the gene.
        :return: The alias_symbols of this GeneDetail.
        :rtype: str
        """
        return self._alias_symbols

    @alias_symbols.setter
    def alias_symbols(self, alias_symbols):
        """Sets the alias_symbols of this GeneDetail.

        Current HGNC alias_symbols for the gene.

        :param alias_symbols: The previous_names of this GeneInfo
        :type alias_symbols: str
        """

        self._alias_symbols = alias_symbols

    @property
    def alias_names(self):
        """Gets the alias_names of this GeneDetail.

        Current HGNC alias_names for the gene.
        :return: The alias_names of this GeneDetail.
        :rtype: str
        """
        return self._alias_names

    @alias_names.setter
    def alias_names(self, alias_names):
        """Sets the alias_names of this GeneDetail.

        Current HGNC alias_names for the gene.

        :param alias_names: The previous_names of this GeneInfo
        :type alias_names: str
        """

        self._alias_names = alias_names

    @property
    def references(self):
        """Gets the references of this GeneDetail.

        References for the gene.
        :return: The references of this GeneDetail.
        :rtype: List[str]
        """
        return self._references

    @references.setter
    def references(self, references):
        """Sets the references of this GeneDetail.

        References for the gene.

        :param references: The references of this GeneInfo
        :type references: str
        """

        self._references = references

    @property
    def summaries(self):
        """Gets the summaries of this GeneDetail.

        RefSeq summary for the gene.
        :return: The summaries of this GeneDetail.
        :rtype: str
        """
        return self._summaries

    @summaries.setter
    def summaries(self, summaries):
        """Sets the summaries of this GeneDetail.

        Current HGNC approved symbol for the gene.

        :param summaries: The approved_symbol of this GeneInfo
        :type summaries: str
        """

        self._summaries = summaries

    @property
    def cell_types_code(self):
        """Gets the cell_types_code of this GeneDetail.

        cell types for the gene.
        :return: The summaries of this GeneDetail.
        :rtype: str
        """
        return self._summaries

    @summaries.setter
    def cell_types_code(self, cell_types_code):
        """Sets the summaries of this GeneDetail.

        Cell types for the gene.

        :param cell_types_code: The approved_symbol of this GeneInfo
        :type cell_types_code: str
        """

        self._cell_types_code = cell_types_code
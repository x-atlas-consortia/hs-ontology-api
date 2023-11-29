# coding: utf-8

# JAS September 2023
# GeneDetail model class
# Used by the genes endpoint.
# Contains information on a gene identified in HGNC.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

# Sub-object models
# Array of gene reference objects
from hs_ontology_api.models.genedetail_reference import GeneDetailReference
# Array of cell type objects
from hs_ontology_api.models.genedetail_celltype import GeneDetailCellType


class GeneDetail(Model):
    def __init__(self, hgnc_id=None, approved_symbol=None, approved_name=None, previous_symbols=None,
                 previous_names=None, alias_symbols=None, alias_names=None, references=None,
                 summaries=None, cell_types_code=None, cell_types_code_name=None, cell_types_code_definition=None,
                 cell_types_codes_organ=None, cell_types_code_source=None):
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
                :param cell_types_code_name: list of names for cell types for the gene
                :type cell_types_code_name: List[str]
                :param cell_types_code_source: list of sources for cell types associations for the gene
                :type cell_types_code_source: List[str]

        """
        #
        # cell_types_code, cell_types_code_name and the cell_types_code_* parameters are used
        # to build a nested objects named cell_types.
        # Cell type information except for CL code is optional. The cell_types_code parameter lists all cell types
        # associated with a gene; the cell_types_code_* parameters contain optional information.

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
            'summary': List[str],
            'cell_types': List[GeneDetailCellType]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'hgnc_id': 'hgnc_id',
            'approved_symbol': 'approved_symbol',
            'approved_name': 'approved_name',
            'previous_symbols': 'previous_symbols',
            'previous_names': 'previous_names',
            'alias_symbols': 'alias_symbols',
            'alias_names': 'alias_names',
            'references': 'references',
            'summary': 'summary',
            'cell_types': 'cell_types'
        }
        # Property assignments
        self._hgnc_id = hgnc_id
        self._approved_symbol = approved_symbol[0]
        self._approved_name = approved_name[0]
        if previous_symbols is None:
            self._previous_symbols = []
        else:
            self._previous_symbols = previous_symbols
        if previous_names is None:
            self._previous_names = []
        else:
            self._previous_names = previous_names
        if alias_symbols is None:
            self._alias_symbols = []
        else:
            self._alias_symbols = alias_symbols
        if alias_names is None:
            self._alias_names = []
        else:
            self._alias_names = alias_names
        if references is None:
            self._references = []
        else:
            self._references = self._makereferencedict(references)
        if summaries is None:
            self._summary = ''
        else:
            self._summary = summaries[0]
        if cell_types_code is None:
            self._cell_types = []
        else:
            self._cell_types = self._makecelltypedict(cell_types_code, cell_types_code_name,
                                                      cell_types_code_definition, cell_types_codes_organ,
                                                      cell_types_code_source)

    def _makereferencedict(self, references=None) -> List[dict]:

        # Builds a list of dictionaries of references for a gene.
        # The references parameter is an optional list of delimited reference codes--e.g., [ENTREZ:X, ENSEMBLE:Y].

        # Each reference code will be expanded to a "reference" JSON object with additional key/value pairs.
        listret = []
        if references is None:
            return []

        for ref in references:
            # Instantiate and populate a "reference" object.
            genedetailref = GeneDetailReference(ref)
            # Use the to_dict method of the Model base class to obtain a dictionary of the reference object..
            dictref = genedetailref.to_dict()
            listret.append(dictref)

        return listret

    def _makecelltypedict(self, cell_types_code=None, cell_types_code_name=None,
                          cell_types_code_definition=None, cell_types_code_organ=None,
                          cell_types_code_source=None) -> List[dict]:

        # Builds a list of dictionaries of cell types associated with a gene.
        # The cell_types_code parameter is an optional list of optional codes from Cell Ontology--e.g., [CL:X, CL:Y].

        # Each cell type code will be expanded to a "cell types" JSON object.
        # For a cell type, all information other than the code (i.e., name, defintion, organ association) is optional.
        # This optional information is stored in the cell_types_code_* parameters and passed to an object of type
        # GeneDetailCellType, which will build nested objects.

        listret = []
        if cell_types_code is None:
            return []

        for cell in cell_types_code:

            # Look for matching optional information for the cell type.
            # The elements in the optional parameters lists are formatted as follows:
            # cell_types_code_name, cell_types_code_definition: CL:CODE|thing
            # cell_types_code_organ: CL:CODE|UBERON:CODE*organ name
            # A cell type will have at most one name or definition, but can be associated with multiple organs--i.e.,
            # the cell_types_code_organ list generally has more than one element.

            name = ''
            definition = ''
            organ_list = []
            source_list = []
            # name
            if cell_types_code_name is not None:
                for nam in cell_types_code_name:
                    cl_code = nam.split('|')[0]
                    if cl_code == cell:
                        name = nam.split('|')[1]
                        break

            # definition
            if cell_types_code_definition is not None:
                for defn in cell_types_code_definition:
                    cl_code = defn.split('|')[0]
                    if cl_code == cell:
                        definition = defn.split('|')[1]
                        break

            # organs
            if cell_types_code_organ is not None:
                for org in cell_types_code_organ:
                    cl_code = org.split('|')[0]
                    if cl_code == cell:
                        # The list of organs is a string delimited as SAB1:CODE1*name1,SAB2:CODE2*name2.
                        # Convert to a list.
                        organ_list = org.split('|')[1].split(',')
            # source

            if cell_types_code_source is not None:
                for source in cell_types_code_source:
                    cl_code = source.split('|')[0]
                    if cl_code == cell:
                        # The list of organs is a string delimited as SAB1:CODE1*name1,SAB2:CODE2*name2.
                        # Convert to a list.
                        source_list = source.split('|')[1].split(',')

            # Instantiate a cell type object.
            genedetailcelltype = GeneDetailCellType(cell, name, definition, organ_list, source_list)
            # Use the to_dict method of the Model base class to obtain a dict for the list.
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
            "summary": self._summary,
            "cell_types": self._cell_types
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

        :param hgnc_id: The approved_id of this GeneInfo
        :type hgnc_id: str
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
        """Gets the previous_symbols of this GeneDetail.

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

        :param alias_symbols: The alias_symbols of this GeneInfo
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

        :param alias_names: The alias_names of this GeneInfo
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
    def summary(self):
        """Gets the summary of this GeneDetail.

        RefSeq summary for the gene.
        :return: The summary of this GeneDetail.
        :rtype: str
        """
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Sets the summary of this GeneDetail.

        RefSeq summary for the gene.

        :param summary: The summary of this GeneInfo
        :type summary: str
        """

        self._summary = summary

    @property
    def cell_types(self):
        """Gets the cell_types of this GeneDetail.

        cell types for the gene.
        :return: The cell_types of this GeneDetail.
        :rtype: str
        """
        return self._cell_types

    @cell_types.setter
    def cell_types(self, cell_types):
        """Sets the cell_types of this GeneDetail.

        Cell types for the gene.

        :param cell_types: The cell_types of this GeneInfo
        :type cell_types: str
        """

        self._cell_types = cell_types

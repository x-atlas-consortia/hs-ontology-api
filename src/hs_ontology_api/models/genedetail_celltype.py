# coding: utf-8

# JAS September 2023
# GeneDetailCellTypes model
# Information on the cell types associated with gene identified in HGNC.

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

# Organ sub-object
from hs_ontology_api.models.genedetail_celltype_organ import GeneDetailCellTypeOrgan


class GeneDetailCellType(Model):
    def __init__(self, id=None, name=None, definition=None, organ_list=None, reference_list=None):
        """GeneDetailCellType - a model defined in OpenAPI
            :param id: the code in Cell Ontology that HRA indicates is associated with a gene (in format CL:CODE)
            :type id: str
            :param name: the optional preferred term for the cell type in Cell Ontology
            :type id: str
            :param definition: the optional definition for the cell type in Cell Ontology
            :type id: str
            :param organ_list: a list of optional organ associations for the cell type in Cell Ontology
            :type id: str
            :param reference_list: a list of optional reference associations for the cell type in Cell Ontology
            :type id: str
        """
        # The parameter organ_list will be used to generate nested objects of type GeneDetailCellTypeOrgan.

        # types
        self.openapi_types = {
            'id': str,
            'name': str,
            'definition': str,
            'organs': List[GeneDetailCellTypeOrgan],
            'references': List[str]
        }
        # attributions
        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'definition': 'definition',
            'organs': 'organs',
            'references': 'references'
        }
        # assignments
        self._id = id
        if name is None:
            self._name = ''
        else:
            self._name = name
        if definition is None:
            self._definition = ''
        else:
            self._definition = definition
        if organ_list is None:
            self._organs = []
        else:
            self._organs = self._makereorgandict(organ_list)
        if reference_list is None:
            self.references = []
        else:
            self._references = reference_list

    def _makereorgandict(self, organs=None) -> List[dict]:

        # Builds a list of organs associated with a cell type.
        # The organs parameter is an optional list of organ reference codes--e.g., [UBERON:X*organ1, UBERON:Y*organ2].

        # Each organ reference code will be expanded to a "reference" JSON object with additional key/value pairs
        listret = []
        # March 2025 expanded to account for case of empty organs list.
        if organs is None or organs == ['']:
            return []

        for organ in organs:
            # Instantiate and populate an organ object.
            # Each organ reference is formatted as SAB:CODE*name--e.g, UBERON:0000948*heart
            source = organ.split(':')[0]
            id = organ.split(':')[1].split('*')[0]
            name = organ.split(':')[1].split('*')[1]
            # Instantiate an organ object using source, id, name.
            organdetail = GeneDetailCellTypeOrgan(source, id, name)
            # Use the to_dict method of the Model base class to obtain a dictionary of the organ object for the list.
            # dictref = organdetail.to_dict()
            listret.append(organdetail)

        return listret

    def serialize(self):
        # Key/value formatting for response.
        return {
            "id": self._id,
            "name": self._name,
            "definition": self._definition,
            "organs": self._organs,
            "references": self._references
        }

    @classmethod
    def from_dict(cls, dikt) -> 'GeneDetailCellType':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GeneDetailReference of this GeneDetailCellType
        :rtype: GeneDetailReference
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this GeneDetailCellType.

        ID for the cell type
        :return: CL code
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the code of this GeneDetailCellType.

        ID for the cell type

        :param id: The CL code
        :type id: str
        """

        self._id = id

    @property
    def name(self):
        """Gets the name of this GeneDetailCellType.

        name for the cell type
        :return: name for the cell type
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this GeneDetailCellType.

        Name for the cell type
        :param name: The CL name
        :type name: str
        """

    @property
    def definition(self):
        """Gets the definition of this GeneDetailCellType.

        definition for the cell type
        :return: definition for the cell type
        :rtype: str
        """
        return self._definition

    @definition.setter
    def definition(self, definition):
        """Sets the definition of this GeneDetailCellType.
        Definition for the CL code

        :param definition: The CL definition
        :type definition: str
        """
        self._definition = definition

    @property
    def organs(self):
        """Gets the organs of this GeneDetailCellType.

        organs for the cell type
        :return: organs for the cell type
        :rtype: str
        """
        return self._organs

    @organs.setter
    def organs(self, organs):
        """Sets the organs of this GeneDetailCellType.
        Organs for the CL code

        :param organs: The CL organs
        :type organs: str
        """
        self._organs = organs

    @property
    def references(self):
        """Gets the references of this GeneDetailCellType.

        References for the cell type association
        :return: references for the cell type association
        :rtype: str
        """
        return self._references

    @references.setter
    def references(self, references):
        """Sets the references of this GeneDetailCellType.
        Reference for the cell type association

        :param references: The source
        :type references: str
        """
        self._references = references

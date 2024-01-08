# coding: utf-8

# JAS December 2023
# FieldAssay model class
# Used by the field-assays endpoint.
# Replicates read of legacy field_assays.yaml.

from __future__ import absolute_import
# from typing import List
# from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util


class FieldAssay:
    def __init__(self, code_ids=None, name=None, assays=None):
        """
        FieldAssay - a model defined in OpenAPI

        Represents associations with metadata fields and assay/datasets.
        Replaces and enhances the legacy field_assays.yaml with additional information related to HUBMAP datasets
        and CEDAR.

        :param code_ids: delimited list of code_ids for the metadata field. The code_ids can come from both
                         HMFIELD or CEDAR.
        :param name: equivalent of the field key in the yaml (HMFIELD) or field name (CEDAR)
        :param assays: delimited list of values in format <assay_identifier>|<data_type>|<dataset_type>.
               Each value in the list has elements:
                - assay_identifier: the assay identifier for the assay from the yaml.
                                    This can be a "not DCWG" (i.e., pre-soft assay) data_type; an alt-name;
                                    or a dataset description used in the Data Portal.
                - data_type: the pre-soft assay data_type, if this is a "not DCWG" assay dataset
                - dataset_type: the "soft assay" dataset type

        example:
        code_ids - [HMFIELD:1008|CEDAR:9f654d25-4de7-4eda-899b-417f05e5d5c3]
        name - acquisition_instrument_model
        assays - [scRNAseq-10xGenomics|scRNAseq-10xGenomics-v3|RNASeq,...]

        The elements in code_ids and assays will be parsed into arrays.
        """

        # Types for JSON objects
        self.openapi_types = {
            'code_ids': list[str],
            'name': str,
            'assays': list[dict]
        }
        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'code_ids': 'code_ids',
            'name': 'name',
            'assays': 'assays'
        }
        # Property assignments

        if name is None:
            self._name = ''
        else:
            self._name = name

        self._code_ids = code_ids.split('|')

        listassays = []
        if assays is not None:
            # If no associated assays were found, the query returns ['none|none|none'].
            for assay in assays:
                if assay.split('|')[0] != 'none':
                    dictassay = {'assay_identifier': assay.split('|')[0], 'data_type': assay.split('|')[1],
                                 'dataset_type': assay.split('|')[2]}
                    listassays.append(dictassay)
        self._assays = listassays

    def serialize(self):
        # Key/value format of response.
        return {
            "code_ids": self._code_ids,
            "name": self.name,
            "assays": self._assays
        }

    @classmethod
    def from_dict(cls, dikt) -> 'FieldAssay':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The FieldAssay of this FieldAssay
        :rtype: FieldAssay
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code_ids(self):
        """Gets the code_ids of this FieldAssay.
        :return: The code_ids for the field from HMFIELD
        :rtype: str
        """
        return self._code_ids

    @code_ids.setter
    def code_id(self, code_ids):
        """Sets the code_ids for the field from HMFIELD

        :param code_ids: The code_id of this field
        :type code_ids: str
        """
        self._code_ids = code_ids

    @property
    def name(self):
        """Gets the name of this FieldAssay.
        :return: The name for the field
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name for the field from HMFIELD

        :para name: The name of this field
        :type name: str
        """
        self._name = name

    @property
    def assays(self):
        """Gets the assays of this FieldAssay.
        :return: The assays for the field from HMFIELD
        :rtype: list[dict]
        """
        return self._assays

    @assays.setter
    def assays(self, assays):
        """Sets the assays for the field

        :param assays: The description of this field
        :type assays: list[dict]
        """
        self._assays = assays

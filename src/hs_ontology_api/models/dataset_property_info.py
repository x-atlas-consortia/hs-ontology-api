from __future__ import absolute_import
from ubkg_api.models.base_model_ import Model

from typing import List


class DatasetPropertyInfo(Model):
    def __init__(self, alt_names=None, contains_pii=None, data_type=None, dataset_provider=None, description=None, primary=None, vis_only=None, vitessce_hints=None):
        """DatasetPropertyInfo - a model defined in OpenAPI

        :param alt_names: The alt_names of this DatasetPropertyInfo.
        :type alt_names: List[str]
        :param contains_pii: The contains_pii of this DatasetPropertyInfo.
        :type contains_pii: str
        :param data_type: The data_type of this DatasetPropertyInfo.
        :type data_type: str
        :param dataset_provider: The dataset_provider of this DatasetPropertyInfo.
        :type dataset_provider: str
        :param description: The description of this DatasetPropertyInfo.
        :type description: str
        :param primary: The primary of this DatasetPropertyInfo.
        :type primary: str
        :param vis_only: The vis_only of this DatasetPropertyInfo.
        :type vis_only: List[str]
        :param vitessce_hints: The vitessce_hints of this DatasetPropertyInfo.
        :type vitessce_hints: List[str]
        """
        self.openapi_types = {
            'alt_names': List[str],
            'contains_pii': str,
            'data_type': str,
            'dataset_provider': str,
            'description': str,
            'primary': str,
            'vis_only': List[str],
            'vitessce_hints': List[str]
        }

        self.attribute_map = {
            'alt_names': 'alt-names',
            'contains_pii': 'contains-pii',
            'data_type': 'data_type',
            'dataset_provider': 'dataset_provider',
            'description': 'description',
            'primary': 'primary',
            'vis_only': 'vis-only',
            'vitessce_hints': 'vitessce-hints'
        }

        self._alt_names = alt_names
        self._contains_pii = contains_pii
        self._data_type = data_type
        self._dataset_provider = dataset_provider
        self._description = description
        self._primary = primary
        self._vis_only = vis_only
        self._vitessce_hints = vitessce_hints

    def serialize(self):
        return {
            "alt-names": self._alt_names,
            "contains-pii": self._contains_pii,
            "data_type": self._data_type,
            "dataset_provider": self._dataset_provider,
            "description": self._description,
            "primary": self._primary,
            "vis-only": self._vis_only,
            "vitessce-hints": self._vitessce_hints
        }

    @classmethod
    def from_dict(cls, dikt) -> 'DatasetPropertyInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The DatasetPropertyInfo of this DatasetPropertyInfo.
        :rtype: DatasetPropertyInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def alt_names(self):
        """Gets the alt_names of this DatasetPropertyInfo.

        Alternative/deprecated synonyms of data_type that may still be associated with dataset entities

        :return: The alt_names of this DatasetPropertyInfo.
        :rtype: List[str]
        """
        return self._alt_names

    @alt_names.setter
    def alt_names(self, alt_names):
        """Sets the alt_names of this DatasetPropertyInfo.

        Alternative/deprecated synonyms of data_type that may still be associated with dataset entities

        :param alt_names: The alt_names of this DatasetPropertyInfo.
        :type alt_names: List[str]
        """

        self._alt_names = alt_names

    @property
    def contains_pii(self):
        """Gets the contains_pii of this DatasetPropertyInfo.

        Whether the dataset contains Patient Identifying Information (PII)

        :return: The contains_pii of this DatasetPropertyInfo.
        :rtype: str
        """
        return self._contains_pii

    @contains_pii.setter
    def contains_pii(self, contains_pii):
        """Sets the contains_pii of this DatasetPropertyInfo.

        Whether the dataset contains Patient Identifying Information (PII)

        :param contains_pii: The contains_pii of this DatasetPropertyInfo.
        :type contains_pii: str
        """

        self._contains_pii = contains_pii

    @property
    def data_type(self):
        """Gets the data_type of this DatasetPropertyInfo.

        Data type for the dataset; used to characterize dataset entities in provenance hierarchy

        :return: The data_type of this DatasetPropertyInfo.
        :rtype: str
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Sets the data_type of this DatasetPropertyInfo.

        Data type for the dataset; used to characterize dataset entities in provenance hierarchy

        :param data_type: The data_type of this DatasetPropertyInfo.
        :type data_type: str
        """

        self._data_type = data_type

    @property
    def dataset_provider(self):
        """Gets the dataset_provider of this DatasetPropertyInfo.

        Identifies the provider of the dataset. 'External Provider' also referred to as 'lab-processed'.

        :return: The dataset_provider of this DatasetPropertyInfo.
        :rtype: str
        """
        return self._dataset_provider

    @dataset_provider.setter
    def dataset_provider(self, dataset_provider):
        """Sets the dataset_provider of this DatasetPropertyInfo.

        Identifies the provider of the dataset. 'External Provider' also referred to as 'lab-processed'.

        :param dataset_provider: The dataset_provider of this DatasetPropertyInfo.
        :type dataset_provider: str
        """

        self._dataset_provider = dataset_provider

    @property
    def description(self):
        """Gets the description of this DatasetPropertyInfo.

        How datasets of the data type are named in the Data Portal.

        :return: The description of this DatasetPropertyInfo.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this DatasetPropertyInfo.

        How datasets of the data type are named in the Data Portal.

        :param description: The description of this DatasetPropertyInfo.
        :type description: str
        """

        self._description = description

    @property
    def primary(self):
        """Gets the primary of this DatasetPropertyInfo.

        Indicates whether the assay is primary (true) or derived (false)

        :return: The primary of this DatasetPropertyInfo.
        :rtype: str
        """
        return self._primary

    @primary.setter
    def primary(self, primary):
        """Sets the primary of this DatasetPropertyInfo.

        Indicates whether the assay is primary (true) or derived (false)

        :param primary: The primary of this DatasetPropertyInfo.
        :type primary: str
        """

        self._primary = primary

    @property
    def vis_only(self):
        """Gets the vis_only of this DatasetPropertyInfo.

        Indicates whether for visualization only

        :return: The vis_only of this DatasetPropertyInfo.
        :rtype: List[str]
        """
        return self._vis_only

    @vis_only.setter
    def vis_only(self, vis_only):
        """Sets the vis_only of this DatasetPropertyInfo.

        Indicates whether for visualization only

        :param vis_only: The vis_only of this DatasetPropertyInfo.
        :type vis_only: List[str]
        """

        self._vis_only = vis_only

    @property
    def vitessce_hints(self):
        """Gets the vitessce_hints of this DatasetPropertyInfo.

        Flags for Vitessce visualization

        :return: The vitessce_hints of this DatasetPropertyInfo.
        :rtype: List[str]
        """
        return self._vitessce_hints

    @vitessce_hints.setter
    def vitessce_hints(self, vitessce_hints):
        """Sets the vitessce_hints of this DatasetPropertyInfo.

        Flags for Vitessce visualization

        :param vitessce_hints: The vitessce_hints of this DatasetPropertyInfo.
        :type vitessce_hints: List[str]
        """

        self._vitessce_hints = vitessce_hints

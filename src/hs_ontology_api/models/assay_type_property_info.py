# coding: utf-8

from __future__ import absolute_import

from typing import List

from ubkg_api.models import util
from ubkg_api.models.base_model_ import Model


class AssayTypePropertyInfo(Model):
    def __init__(self, name=None, primary=None, description=None, vitessce_hints=None, contains_pii=None, vis_only=None):
        """AssayTypePropertyInfo - a model defined in OpenAPI

        :param name: The name of this AssayTypePropertyInfo.
        :type name: str
        :param primary: The primary of this AssayTypePropertyInfo.
        :type primary: bool
        :param description: The description of this AssayTypePropertyInfo.
        :type description: str
        :param vitessce_hints: The vitessce_hints of this AssayTypePropertyInfo.
        :type vitessce_hints: List[str]
        :param contains_pii: The contains_pii of this AssayTypePropertyInfo.
        :type contains_pii: bool
        :param vis_only: The vis_only of this AssayTypePropertyInfo.
        :type vis_only: List[bool]
        """
        self.openapi_types = {
            'name': str,
            'primary': bool,
            'description': str,
            'vitessce_hints': List[str],
            'contains_pii': bool,
            'vis_only': List[bool]
        }

        self.attribute_map = {
            'name': 'name',
            'primary': 'primary',
            'description': 'description',
            'vitessce_hints': 'vitessce-hints',
            'contains_pii': 'contains-pii',
            'vis_only': 'vis-only'
        }

        self._name = name
        self._primary = primary
        self._description = description
        self._vitessce_hints = vitessce_hints
        self._contains_pii = contains_pii
        self._vis_only = vis_only

    def serialize(self):
        return {
            "name": self._name,
            "primary": self._primary,
            "description": self._description,
            "vitessce_hints": self._vitessce_hints,
            "contains_pii": self._contains_pii,
            "vis_only": self._vis_only
        }

    @classmethod
    def from_dict(cls, dikt) -> 'AssayTypePropertyInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AssayTypePropertyInfo of this AssayTypePropertyInfo.
        :rtype: AssayTypePropertyInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self):
        """Gets the name of this AssayTypePropertyInfo.

        AssayType name; used to characterize dataset entities in provenance hierarchy

        :return: The name of this AssayTypePropertyInfo.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this AssayTypePropertyInfo.

        AssayType name; used to characterize dataset entities in provenance hierarchy

        :param name: The name of this AssayTypePropertyInfo.
        :type name: str
        """

        self._name = name

    @property
    def primary(self):
        """Gets the primary of this AssayTypePropertyInfo.

        Indicates whether the assay is primary (true) or derived (false)

        :return: The primary of this AssayTypePropertyInfo.
        :rtype: bool
        """
        return self._primary

    @primary.setter
    def primary(self, primary):
        """Sets the primary of this AssayTypePropertyInfo.

        Indicates whether the assay is primary (true) or derived (false)

        :param primary: The primary of this AssayTypePropertyInfo.
        :type primary: bool
        """

        self._primary = primary

    @property
    def description(self):
        """Gets the description of this AssayTypePropertyInfo.

        How datasets of the data type are named in the Data Portal.

        :return: The description of this AssayTypePropertyInfo.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this AssayTypePropertyInfo.

        How datasets of the data type are named in the Data Portal.

        :param description: The description of this AssayTypePropertyInfo.
        :type description: str
        """

        self._description = description

    @property
    def vitessce_hints(self):
        """Gets the vitessce_hints of this AssayTypePropertyInfo.

        Flags for Vitessce visualization

        :return: The vitessce_hints of this AssayTypePropertyInfo.
        :rtype: List[str]
        """
        return self._vitessce_hints

    @vitessce_hints.setter
    def vitessce_hints(self, vitessce_hints):
        """Sets the vitessce_hints of this AssayTypePropertyInfo.

        Flags for Vitessce visualization

        :param vitessce_hints: The vitessce_hints of this AssayTypePropertyInfo.
        :type vitessce_hints: List[str]
        """

        self._vitessce_hints = vitessce_hints

    @property
    def contains_pii(self):
        """Gets the contains_pii of this AssayTypePropertyInfo.

        Whether the dataset contains Patient Identifying Information (PII) (true or false)

        :return: The contains_pii of this AssayTypePropertyInfo.
        :rtype: bool
        """
        return self._contains_pii

    @contains_pii.setter
    def contains_pii(self, contains_pii):
        """Sets the contains_pii of this AssayTypePropertyInfo.

        Whether the dataset contains Patient Identifying Information (PII) (true or false)

        :param contains_pii: The contains_pii of this AssayTypePropertyInfo.
        :type contains_pii: bool
        """

        self._contains_pii = contains_pii

    @property
    def vis_only(self):
        """Gets the vis_only of this AssayTypePropertyInfo.

        Indicates whether for visualization only (true or false)

        :return: The vis_only of this AssayTypePropertyInfo.
        :rtype: List[bool]
        """
        return self._vis_only

    @vis_only.setter
    def vis_only(self, vis_only):
        """Sets the vis_only of this AssayTypePropertyInfo.

        Indicates whether for visualization only (true or false)

        :param vis_only: The vis_only of this AssayTypePropertyInfo.
        :type vis_only: List[bool]
        """

        self._vis_only = vis_only

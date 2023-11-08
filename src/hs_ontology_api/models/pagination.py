# coding: utf-8

# JAS November 2023
# Pagination model class
# Used by the *s-info endpoints--e.g., genes-info, proteins-info

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class Pagination():

    def __init__(self, page=None, totalpages=None, itemsperpage=None, startswith=None, itemcount=None):
        """Pagination - a model defined in OpenAPI

        :param page: Relative "page" (block of items)
        :param totalpages: Total number of "pages" (blocks of items)
        :param itemsperpage: Number of items in each "page" (block)
        :param startswith: Optional search string for type ahead
        :param itemcount: Count of items, optionally filtered by startswith

        """

        # Types for JSON objects
        self.openapi_types = {
            'page': int,
            'totalpages': int,
            'itemsperpage': int,
            'startswith': str,
            'itemcount': int
        }

        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'page': 'page',
            'totalpages': 'totalpages',
            'itemsperpage': 'itemsperpage',
            'startswith': 'startswith',
            'itemcount': 'itemcount'
        }
        # Property assignments
        self._page = int(page)
        self._totalpages = int(totalpages)
        self._itemsperpage = int(itemsperpage)
        self._startswith = startswith
        self._itemcount = itemcount

    def serialize(self):
        # Key/value format of response.
        return {
            "page": self._page,
            "totalpages": self._totalpages,
            "genes_per_page": self._itemsperpage,
            "startswith": self._startswith,
            "itemcount": self._itemcount
        }

    @classmethod
    def from_dict(cls, dikt) -> 'Pagination':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The class
        :rtype: GeneDetail
        """
        return util.deserialize_model(dikt, cls)

    def serialize(self):
        # Key/value format of response.
        return {
            "page": self._page,
            "totalpages": self._totalpages,
            "itemsperpage": self._itemsperpage,
            "startswith": self._startswith,
            "itemcount": self._itemcount
        }

    @property
    def page(self):
        """Gets the page of this Pagination.

        'Page' or relative block of items.
        :return: The page of this Pagination.
        :rtype: str
        """
        return self._page

    @page.setter
    def page(self, page):
        """Sets the page of this Pagination.

        'Page' or relative block of items.

        :param page: The page of this Pagination
        :type page: str
        """

        self._page = page

    @property
    def totalpages(self):
        """Gets the total_pages of this Pagination.

        Total number of "pages" (blocks of items)
        :return: The total_pages of this Pagination.
        :rtype: int
        """
        return self._totalpages

    @totalpages.setter
    def total_pages(self, totalpages):
        """Sets the total_pages of this Pagination.

        Total number of "pages" (blocks of items)

        :param totalpages: The number of itmes in this Pagination
        :type genes: int
        """

        self._totalpages = totalpages

    @property
    def itemsperpage(self):
        """Gets the itemsperpage of this Pagination.

        Number of items per "page" or block of returns
        :return: The itemsperpage of this Pagination.
        :rtype: int
        """
        return self._itemsperpage

    @itemsperpage.setter
    def genes_per_page(self, itemsperpage):
        """Sets the itemsperpage of this Pagination.

        Number of items per "page" or block of returns

        :param itemsperpage: The itemsperpage of this Pagination
        :type itemsperpage: int
        """

        self._itemsperpage = itemsperpage

    @property
    def startswith(self):
        """Gets the startswith of this Pagination.

        Optional type-ahead search string
        :return: The startswith of this Pagination.
        :rtype: str
        """
        return self._startswith

    @startswith.setter
    def startswith(self, startswith):
        """Sets the startswith of this Pagination.

        Optional type-ahead search string

        :param starts_with: The startswith of this Pagination
        :type startswith: int
        """

        self._startswith = startswith

    @property
    def itemcount(self):
        """Gets the itemcount of this Pagination.

        Count of items, optionally filtered by startswith.
        :return: The itemcount of this Pagination.
        :rtype: str
        """
        return self._itemcount

    @itemcount.setter
    def itemcount(self, itemcount):
        """Sets the itemcount of this Pagination.

        Count of items, optionally filtered by startswith

        :param itemcount: The itemcount of this Pagination
        :type itemcount: int
        """

        self._itemcount = itemcount
# coding: utf-8

# JAS November 2023
# Pagination model class
# Used by the *s-info endpoints--e.g., genes-info, proteins-info

from __future__ import absolute_import
from typing import List
from ubkg_api.models.base_model_ import Model
from ubkg_api.models import util

class Pagination():

    def __init__(self, page=None, total_pages=None, items_per_page=None, starts_with=None, item_count=None):
        """Pagination - a model defined in OpenAPI

        :param page: Relative "page" (block of items)
        :param total_pages: Total number of "pages" (blocks of items)
        :param items_per_page: Number of items in each "page" (block)
        :param starts_with: Optional search string for type ahead
        :param item_count: Count of items, optionally filtered by starts_with

        """

        # Types for JSON objects
        self.openapi_types = {
            'page': int,
            'total_pages': int,
            'items_per_page': int,
            'starts_with': str,
            'item_count': int
        }

        # Attribute mappings used by the base Model class to assert key/value pairs.
        self.attribute_map = {
            'page': 'page',
            'total_pages': 'total_pages',
            'items_per_page': 'items_per_page',
            'starts_with': 'starts_with',
            'item_count': 'item_count'
        }
        # Property assignments
        self._page = int(page)
        self._total_pages = int(total_pages)
        self._items_per_page = int(items_per_page)
        self._starts_with = starts_with
        self._item_count = item_count

    def serialize(self):
        # Key/value format of response.
        return {
            "page": self._page,
            "total_pages": self._total_pages,
            "genes_per_page": self._items_per_page,
            "starts_with": self._starts_with,
            "item_count": self._item_count
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
            "total_pages": self._total_pages,
            "items_per_page": self._items_per_page,
            "starts_with": self._starts_with,
            "item_count": self._item_count
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
    def total_pages(self):
        """Gets the total_pages of this Pagination.

        Total number of "pages" (blocks of items)
        :return: The total_pages of this Pagination.
        :rtype: int
        """
        return self._total_pages

    @total_pages.setter
    def total_pages(self, total_pages):
        """Sets the total_pages of this Pagination.

        Total number of "pages" (blocks of items)

        :param total_pages: The number of itmes in this Pagination
        :type genes: int
        """

        self._total_pages = total_pages

    @property
    def items_per_page(self):
        """Gets the items_per_page of this Pagination.

        Number of items per "page" or block of returns
        :return: The items_per_page of this Pagination.
        :rtype: int
        """
        return self._items_per_page

    @items_per_page.setter
    def genes_per_page(self, items_per_page):
        """Sets the items_per_page of this Pagination.

        Number of items per "page" or block of returns

        :param items_per_page: The items_per_page of this Pagination
        :type items_per_page: int
        """

        self._items_per_page = items_per_page

    @property
    def starts_with(self):
        """Gets the starts_with of this Pagination.

        Optional type-ahead search string
        :return: The starts_with of this Pagination.
        :rtype: str
        """
        return self._starts_with

    @starts_with.setter
    def starts_with(self, starts_with):
        """Sets the starts_with of this Pagination.

        Optional type-ahead search string

        :param starts_with: The starts_with of this Pagination
        :type starts_with: int
        """

        self._starts_with = starts_with

    @property
    def item_count(self):
        """Gets the item_count of this Pagination.

        Count of items, optionally filtered by starts_with.
        :return: The item_count of this Pagination.
        :rtype: str
        """
        return self._item_count

    @item_count.setter
    def item_count(self, item_count):
        """Sets the item_count of this Pagination.

        Count of items, optionally filtered by starts_with

        :param item_count: The item_count of this Pagination
        :type item_count: int
        """

        self._item_count = item_count
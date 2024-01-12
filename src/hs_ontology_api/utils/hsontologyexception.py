# coding: utf-8

# Custom error class
class hsontologyError(Exception):
    """A base class for hs-ontology-api exceptions."""

class DuplicateFieldError(hsontologyError):
   """A custom exception class to handle the case in which a filtered query returns more than one value."""

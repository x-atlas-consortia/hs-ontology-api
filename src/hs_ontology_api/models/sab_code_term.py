from __future__ import absolute_import

from ubkg_api.models.base_model_ import Model


class SabCodeTerm(Model):
    def __init__(self, sab=None, code=None, term=None):
        """SabCodeTerm - a model defined in OpenAPI

        :param sab: The sab of this SabCodeTerm.
        :type sab: str
        :param code: The code of this SabCodeTerm.
        :type code: str
        :param term: The term of this SabCodeTerm.
        :type term: str
        """
        self.openapi_types = {
            'sab': str,
            'code': str,
            'term': str
        }

        self.attribute_map = {
            'sab': 'sab',
            'code': 'code',
            'term': 'term'
        }

        self._sab = sab
        self._code = code
        self._term = term

    @classmethod
    def from_dict(cls, dikt) -> 'SabCodeTerm':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The SabCodeTerm of this SabCodeTerm.
        :rtype: SabCodeTerm
        """
        return util.deserialize_model(dikt, cls)

    @property
    def sab(self):
        """Gets the sab of this SabCodeTerm.


        :return: The sab of this SabCodeTerm.
        :rtype: str
        """
        return self._sab

    @sab.setter
    def sab(self, sab):
        """Sets the sab of this SabCodeTerm.


        :param sab: The sab of this SabCodeTerm.
        :type sab: str
        """

        self._sab = sab

    @property
    def code(self):
        """Gets the code of this SabCodeTerm.


        :return: The code of this SabCodeTerm.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this SabCodeTerm.


        :param code: The code of this SabCodeTerm.
        :type code: str
        """

        self._code = code

    @property
    def term(self):
        """Gets the term of this SabCodeTerm.


        :return: The term of this SabCodeTerm.
        :rtype: str
        """
        return self._term

    @term.setter
    def term(self, term):
        """Sets the term of this SabCodeTerm.


        :param term: The term of this SabCodeTerm.
        :type term: str
        """

        self._term = term

    def serialize(self):
        return {
            "code": self._code,
            "sab": self._sab,
            "term": self._term
        }

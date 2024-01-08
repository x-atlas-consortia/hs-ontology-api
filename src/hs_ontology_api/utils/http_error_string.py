# coding: utf-8
# Common functions used for format HTTP error messages (404, 400) for endpoints.

from flask import request


def get_404_error_string(prompt_string=None):
    """
    Formats an error string for a 404 response, accounting for optional parameters.
    :param: prompt_string - optional description of error
    :return: string
    """
    if prompt_string is None:
        err = "No values for "
    else:
        err = prompt_string

    # The request path will be one of three types:
    # 1. The final element will correspond to the endpoint (e.g., /field-descriptions)
    # 2. The penultimate element will correspond to the endpoint, and the final element will be a filter.
    pathsplit = request.path.split('/')
    err = err + f"{pathsplit[0]} "
    if len(pathsplit) > 3:
        err = err + f" for path {request.path}"
    elif len(pathsplit) == 3:
        err = err + f" for '{pathsplit[2]}'"
    else:
        err = err + f" for '{pathsplit[1]}'"

    listerr = []
    for req in request.args:
        listerr.append(f"'{req}'='{request.args[req]}'")

    if len(listerr) > 0:
        err = err + ' and query parameter'
        if len(listerr) > 1:
            err = err + 's'
        err = err + ' ' + ' ; '.join(listerr) + '.'

    return err


def get_number_agreement(list_items=None):
    """
    Builds a clause with correct number agreement
    :param list_items: list of items
    :return:
    """
    if len(list_items) < 2:
        return ' is'
    else:
        return 's are'


def list_as_single_quoted_string(delim: str = ';', list_elements=None):
    """Converts the list of elements in list_elements into a string formatted with single quotes--
    e.g., ['a','b','c'] -> "'a'; 'b'; 'c'"

    """
    return f'{delim} '.join(f"'{x}'" for x in list_elements)


def validate_query_parameter_names(parameter_name_list=None):
    """
    Validates query parameter names in the querystring. Prepares the content of a 404 message if the
    querystring includes an unexpected parameter.
    :param parameter_name_list:
    :return:
    - "ok"
    - error string for a 400 error
    """

    for req in request.args:
        if req not in parameter_name_list:
            namelist = list_as_single_quoted_string(list_elements=parameter_name_list)
            prompt = get_number_agreement(parameter_name_list)
            return f"Invalid query parameter: '{req}'. The possible parameter name{prompt}: {namelist}. " \
                   f"Refer to the SmartAPI documentation for this endpoint for more information."

    return "ok"


def validate_parameter_value_in_enum(param_name=None, param_value=None, enum_list=None):
    """
    Verifies that a parameter's value is a member of a defined set--i.e., the equivalent of in an enumeration.
    :param enum_list: list of enum values
    :param param_value: value to validate
    :param param_name: parameter name
    :return:
    --"ok"
    --error string suitable for a 400 message
    """

    if param_value is None:
        return "ok"

    if param_name is None:
        return "ok"

    if param_value not in enum_list:
        namelist = list_as_single_quoted_string(list_elements=enum_list)
        prompt = get_number_agreement(enum_list)
        return f"Invalid value for parameter: '{param_name}'. The possible parameter value{prompt}: {namelist}. " \
               f"Refer to the SmartAPI documentation for this endpoint for more information."

    return "ok"

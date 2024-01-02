# coding: utf-8
# Common functions used by field_* endpoints.

from flask import request

def get_error_string(field_name=None,prompt_string=None):
    """
    Formats an error string for a 404 response, accounting for optional parameters.

    :param field_name: field name (used in the field-*/<name> route)
    :return: string
    """

    if prompt_string is None:
        err = "Error "
    else:
        err = prompt_string

    if field_name is not None:
        listerr = [f"field_name='{field_name}'"]
    else:
        listerr = []

    for req in request.args:
        listerr.append(f"{req}='{request.args[req]}'")

    if len(listerr) > 0:
        err = err + ' for query parameters: ' + '; '.join(listerr) + '.'

    return err
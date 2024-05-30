# Utilities for handling common hs-ontology-api endpoint parameters.

from flask import request

from ubkg_api.utils.http_error_string import validate_required_parameters, validate_query_parameter_names,\
    get_404_error_string, validate_parameter_value_in_enum


def validate_application_context(param_value=None) -> str:
    """
    Validates the application context.
    Assumes that the application context parameter is named 'application_context', which should be the case
    for hs-ontology-api endpoints.

    :param param_value: value of the application context parameter.
    """

    err = validate_required_parameters(required_parameter_list=['application_context'])
    if err != 'ok':
        return err

    param_value = param_value.upper()
    val_enum = ['HUBMAP', 'SENNET']
    return validate_parameter_value_in_enum(param_name='application_context', param_value=param_value,
                                            enum_list=val_enum)

def set_active_status_default() -> str:
    """
    Sets the default for active_status
    """
    # DEFAULT: all
    active_status = request.args.get('active_status')
    if active_status is None:
        active_status = 'all'
    else:
        active_status = active_status.lower()

    return active_status

def validate_active_status(param_value=None) -> str:
    """
    Validates the active_status parameter, which is common to a number of endpoints.
    If the parameter is not specified, sets the default value.
    """

    val_enum = ['active', 'inactive', 'all', 'null']
    return validate_parameter_value_in_enum(param_name='active_status', param_value=param_value,
                                           enum_list=val_enum)

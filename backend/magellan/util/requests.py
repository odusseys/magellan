from flask import request, g
from magellan.util.exceptions import BadRequest


def get_value(key: str, default=None):
    """
    get the value associated with key from the request by trying request.args, request.json, request.form and
    request.cookies
    :param key: str
    :param default: the default value to return if no value was found in the resources
    :return: string key if found, None otherwise
    """

    # check query string parameters
    if request.args:
        val = request.args.get(key)
        if val is not None:
            return val

    # cache the json body if present for future calls to get_value in post requests
    try:
        json_data = g.json_data
    except AttributeError:
        g.json_data = request.get_json(force=True, silent=True)
        if g.json_data is None:
            g.json_data = {}
        json_data = g.json_data

    # check the body
    val = json_data.get(key)
    if val is not None:
        return val

    # check form data
    if request.form:
        val = request.form.get(key)
        if val is not None:
            return val

    return default


def get_required_value(key: str):
    value = get_value(key)
    if value is None:
        raise BadRequest("Value not found : {}".format(key),
                         "MISSING_{}".format(key.upper()))
    return value

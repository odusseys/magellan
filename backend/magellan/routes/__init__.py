from flask import Blueprint, jsonify
from magellan.util.exceptions import APIError
from magellan.services.logging import get_logger

LOGGER = get_logger(__name__)

magellan = Blueprint("magellan", __name__)


@magellan.errorhandler(APIError)
def handle_invalid_usage(error: APIError):
    response = jsonify(
        dict(error_code=error.error_code, message=error.message))
    response.status_code = error.status_code
    LOGGER.info(" >>> error {} : {}".format(error.error_code, error.message))
    return response


if True:  # because autopep8 likes moving shit around ...
    from magellan.routes.health import *
    from magellan.routes.admin import *
    from magellan.routes.app import *

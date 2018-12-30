from flask import request, jsonify, g

from magellan.routes import magellan
from magellan.logic.auth import send_verification_text, login_user, signup_user, user_auth, delete_user, reset_phone_number
from magellan.util.requests import get_required_value
from magellan.util.exceptions import BadRequest

@magellan.route("/app/auth/signup", methods=["POST"])
@magellan.route("/v1/app/auth/signup", methods=["POST"])
def signup_app_user_endpoint():
    name = get_required_value("name")
    age = get_required_value("age")
    try:
        age = int(age)
    except ValueError:
        raise BadRequest("Age should be an integer", "INVALID_AGE")
    verification_code = get_required_value("verification_code")
    return jsonify(signup_user(phone_number, name, gender_id, age, verification_code))


@magellan.route("/app/auth/login", methods=["GET"])
@magellan.route("/v1/app/auth/login", methods=["GET"])
def login_app_user_endpoint():
    phone_number = get_required_value("phone_number")
    verification_code = get_required_value("verification_code")
    return jsonify(login_user(phone_number, verification_code))


@magellan.route("/app/auth/account", methods=["DELETE"])
@magellan.route("/v1/app/auth/account", methods=["DELETE"])
@user_auth
def delete_app_user_endpoint():
    delete_user(g.user_id)
    return jsonify(dict(success=True))

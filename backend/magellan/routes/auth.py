from flask import request, jsonify, g

from magellan.routes import magellan
from magellan.logic.auth import create_user, login_user, signup_user, user_auth
from magellan.util.requests import get_required_value
from magellan.util.exceptions import BadRequest


@magellan.route("/auth/invite", methods=["POST"])
def signup_app_user_endpoint():
    first_name = get_required_value("first_name")
    last_name = get_required_value("last_name")
    email = get_required_value("email")
    password = get_required_value("password")
    return jsonify(create_user(first_name, last_name, email, password))


@playground.route("/auth/signup", methods=["POST"])
def signup_user_endpoint():
    invitation_token = get_required_value("invitation_token")
    password = get_required_value("password")
    return jsonify(signup_user(invitation_token, password))


@playground.route("/admin/auth/login", methods=["GET"])
def login_user_endpoint():
    email = get_required_value("email")
    password = get_required_value("password")
    return jsonify(login_user(email, password))

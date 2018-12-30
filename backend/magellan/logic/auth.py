
import re
import jwt
from passlib.hash import pbkdf2_sha256
from functools import wraps
from flask import request

from magellan.services.mail import send_mail
from magellan.models import Account, User
from magellan.services.database import session_scope
from magellan.env import APP_JWT_SECRET
from magellan.util.exceptions import BadRequest, Unauthorized, Conflict
from magellan.services.logging import get_logger

LOGGER = get_logger(__name__)


def create_user(first_name: str, last_name: str, email: str):
    with session_scope() as session:
        user = session.query(User).filter(
            User.email == email).first()
        if user is not None:
            raise Conflict("EMAIL_IN_USE")
        user = User(first_name=first_name,
                         last_name=last_name, email=email)
        session.add(user)
        session.flush()
        payload = dict(user_id=user.id)
        invitation_token = jwt.encode(
            payload, APP_JWT_SECRET, algorithm='HS256').decode('utf-8')
        send_mail([email], "Your Magellan invite",
                      f"Follow the following link:\n\nhttps://admin.magellan-app.io/signup?invitation_token={invitation_token}")
        return dict(invitation_token=invitation_token)


def signup_user(invitation_token: str, password: str):
    if len(password) < 6:
        raise BadRequest(
            "Password should be at least 6 characters long", "PASSWORD_TOO_SHORT")
    try:
        decoded = jwt.decode(
            invitation_token, ADMIN_JWT_SECRET, algorithms=['HS256'])
        user_id = decoded["user_id"]
    except (jwt.exceptions.PyJWTError, KeyError):
        LOGGER.info(f"Received invalid token : {invitation_token}")
        raise Unauthorized(error_code="TOKEN_PARSE_ERROR")
    with session_scope() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise Unauthorized(error_code="USER_NOT_FOUND")
        hashed_password = pbkdf2_sha256.hash(password)
        account = Account(
            user_id=user_id, hashed_password=hashed_password)
        session.add(account)
        session.flush()
        token = jwt.encode(dict(account_id=account.id,
                                user_id=user.id), ADMIN_JWT_SECRET, algorithm='HS256').decode('utf-8')
        return dict(first_name=user.first_name, last_name=user.last_name, token=token)


def user_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth is None:
            raise Unauthorized(error_code="NO_AUTHORIZATION_HEADER")
        match = re.search("^Bearer (.*)$", auth)
        if match is None:
            raise Unauthorized(error_code="INVALID_AUTHORIZATION_HEADER")
        token = match.group(1)
        try:
            payload = jwt.decode(token, ADMIN_JWT_SECRET, algorithms=['HS256'])
        except jwt.exceptions.PyJWTError:
            raise Unauthorized(error_code="INVALID_TOKEN_FORMAT")
        if "account_id" not in payload:
            raise Unauthorized(error_code="INVALID_TOKEN")

        return f(*args, **kwargs)

    return wrapper


def login_user(email: str, password: str):
    with session_scope() as session:
        res = session.query(User, Account).filter(
            User.email == email,
            User.id == Account.user_id
        ).first()
        if res is None:
            raise Unauthorized(error_code="USER_NOT_FOUND")
        user, account = res
        if not pbkdf2_sha256.verify(password, account.hashed_password):
            raise Unauthorized(error_code="INVALID_PASSWORD")
        token = jwt.encode(dict(account_id=account.id,
                                user_id=user.id), ADMIN_JWT_SECRET, algorithm='HS256').decode('utf-8')
        return dict(first_name=user.first_name, last_name=user.last_name, token=token)


def list_users():
    with session_scope() as session:
        res = session.query(User, Account).outerjoin(
            Account).all()
        return [dict(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            registered=account is not None
        ) for user, account in res]

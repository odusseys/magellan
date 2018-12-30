from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from magellan.services.logging import get_logger
from contextlib import contextmanager

LOGGER = get_logger(__name__)

db = SQLAlchemy()


def transactional(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
            db.session.commit()
            return res
        except:
            db.session.rollback()
            LOGGER.exception("Error in transaction")
            raise
    return wrapper


@contextmanager
def session_scope(commit=True, flush=True):
    """Provide a transactional scope around a series of operations."""
    try:
        yield db.session
        if commit:
            db.session.commit()
        elif flush:
            db.session.flush()
    except:
        db.session.rollback()
        LOGGER.exception("Error in transaction")
        raise


def read():
    return session_scope(commit=False, flush=False)


def write():
    return session_scope()

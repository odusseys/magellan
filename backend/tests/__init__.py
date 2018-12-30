import os
import unittest

import pytest
from psycopg2 import connect, ProgrammingError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# mocks: it is imperative to import this before any other magellan modules,
# to make sure the mocks are created correctly. Eventually it would be best
# to do proper monkeypatching with fixtures
import tests.mock.sms as sms
import tests.mock.mail as mail
import tests.mock.s3 as s3
import tests.mock.notifications as notifications

from magellan.app import get_app
from magellan.services.redis import redis


app = get_app()

DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_USER = os.environ["DATABASE_USER"]
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]


def _create_db(cur, name):
    try:
        cur.execute('DROP DATABASE {}'.format(name))
    except ProgrammingError:
        pass
    try:
        cur.execute('CREATE DATABASE {}'.format(name))
    except ProgrammingError:
        pass
    con = connect(dbname=name, user=DATABASE_USER,
                  host=DATABASE_HOST, password=DATABASE_PASSWORD)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur2 = con.cursor()
    cur2.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    cur2.close()
    con.close()


def create_databases():

    con = connect(dbname='postgres', user=DATABASE_USER,
                  host=DATABASE_HOST, password=DATABASE_PASSWORD)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    _create_db(cur, "users")

    cur.close()
    con.close()
    from magellan.services.database import db
    import magellan.models
    db.create_all()


create_databases()


def _clear_db():
    from magellan.services.database import db
    db.session.commit()
    meta = db.metadata
    con = connect(dbname='users', user=DATABASE_USER,
                  host=DATABASE_HOST, password=DATABASE_PASSWORD)

    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    for table in reversed(meta.sorted_tables):
        cur.execute(
            'TRUNCATE TABLE "{}" RESTART IDENTITY CASCADE'.format(table))
    cur.close()
    con.close()


class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

    def tearDown(self):
        _clear_db()
        sms.delete_all()
        mail.delete_all()
        s3.delete_all()
        redis.delete_all()
        notifications.delete_all()

from tests import TestCase
from magellan.services.database import session_scope
from magellan.models import Gender, Interest, Rating, Activity
from magellan.logic.app.auth import send_verification_text, signup_user

PHONE_NUMBER = "+33600000000"
NAME = "Test"
GENDER_ID = 1
AGE = 25

PHONE_NUMBER_2 = "+33600000001"
NAME_2 = "Test2"
GENDER_ID_2 = 2
AGE_2 = 30


class AppAuthTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(AppAuthTestCase, self).__init__(*args, **kwargs)
        self.token = None
        self.user_id = None

    def setUp(self):
        super(AppAuthTestCase, self).setUp()
        with session_scope() as session:
            session.add(Gender(name="male"))
            session.add(Gender(name="female"))
            session.add(Interest(name="a"))
            session.add(Interest(name="b"))
            session.add(Rating(name="x"))
            session.add(Rating(name="y"))
            session.add(Activity(name="test"))
            session.add(Activity(name="test2"))
        code = send_verification_text(PHONE_NUMBER)
        res = signup_user(PHONE_NUMBER, NAME, GENDER_ID, AGE, code)
        self.token = res["token"]
        self.user_id = res["id"]

    def tearDown(self):
        super(AppAuthTestCase, self).tearDown()
        self.token = None


class TwoUserTestCase(AppAuthTestCase):
    def __init__(self, *args, **kwargs):
        super(TwoUserTestCase, self).__init__(*args, **kwargs)
        self.token_2 = None
        self.user_id_2 = None

    def setUp(self):
        super(TwoUserTestCase, self).setUp()
        code = send_verification_text(PHONE_NUMBER_2)
        res = signup_user(PHONE_NUMBER_2, NAME_2, GENDER_ID_2, AGE_2, code)
        self.token_2 = res["token"]
        self.user_id_2 = res["id"]

    def tearDown(self):
        super(TwoUserTestCase, self).tearDown()
        self.token_2 = None
        self.user_id_2 = None

from tests import TestCase
from magellan.env import APP_JWT_SECRET
from magellan.logic.app.auth import send_verification_text, signup_user, delete_user, login_user
from magellan.services.database import session_scope
from magellan.models import User, UserAccount, Gender
from tests.mock.sms import get_messages
from magellan.util.exceptions import Unauthorized
from tests.app import PHONE_NUMBER, GENDER_ID, AGE, NAME, AppAuthTestCase
from tests.requests import put, delete


class TestAuth(TestCase):

    def test_verification(self):
        send_verification_text(PHONE_NUMBER)
        self.assertEqual(len(get_messages(PHONE_NUMBER)), 1)

    def test_signup(self):
        with session_scope() as session:
            session.add(Gender(name="male"))
        code = send_verification_text(PHONE_NUMBER)
        res = signup_user(PHONE_NUMBER, NAME, GENDER_ID, AGE, code)
        self.assertIsNotNone(res.get("token"))
        with session_scope() as session:
            account = session.query(UserAccount).first()
            self.assertIsNotNone(account)
            self.assertEqual(account.phone_number, PHONE_NUMBER)
            user = session.query(User).first()
            self.assertEqual(user.name, NAME)
            self.assertEqual(user.age, AGE)
            self.assertEqual(user.gender_id, GENDER_ID)

    def test_login(self):
        with session_scope() as session:
            session.add(Gender(name="male"))
        code = send_verification_text(PHONE_NUMBER)
        signup_user(PHONE_NUMBER, NAME, GENDER_ID, AGE, code)
        res = login_user(PHONE_NUMBER, code)
        self.assertIsNotNone(res.get("token"))

    def test_login_no_signup(self):
        code = send_verification_text(PHONE_NUMBER)
        self.assertRaises(Unauthorized, login_user, PHONE_NUMBER, code)


class AccountOperationTests(AppAuthTestCase):

    def test_reset_phone(self):
        new_phone = "+4444444444"
        code = send_verification_text(new_phone)
        res = put("/app/auth/phone", dict(
            phone_number=new_phone,
            verification_code=code
        ), self.token)
        self.assertEqual(res.status_code, 200)

    def test_delete_account(self):
        res = delete("/app/auth/account", None, self.token)
        self.assertEqual(res.status_code, 200)
        with session_scope() as session:
            self.assertIsNone(session.query(User).first())
            self.assertIsNone(session.query(UserAccount).first())

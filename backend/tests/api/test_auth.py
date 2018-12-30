from tests import TestCase
from magellan.env import ADMIN_JWT_SECRET
from magellan.logic.admin.auth import create_user, signup_user, login_user
from magellan.services.database import session_scope
from magellan.models import AdminUser, AdminAccount
from tests.requests import post

EMAIL = "test@test.test"
PASSWORD = "testtest"
FIRST_NAME = "First"
LAST_NAME = "Second"


class TestAuth(TestCase):

    def test_create_user(self):
        res = create_user(
            FIRST_NAME, LAST_NAME, EMAIL, False)
        self.assertIsNotNone(res.get("invitation_token"))
        with session_scope() as session:
            user = session.query(AdminUser).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.first_name, FIRST_NAME)
            self.assertEqual(user.last_name, LAST_NAME)
            self.assertEqual(user.email, EMAIL)

    def test_signup(self):
        invitation_token = create_user(
            FIRST_NAME, LAST_NAME, EMAIL, False)["invitation_token"]
        res = signup_user(invitation_token, PASSWORD)
        self.assertEqual(res["first_name"], FIRST_NAME)
        self.assertEqual(res["first_name"], FIRST_NAME)
        self.assertIsNotNone(res["token"])

    def test_login(self):
        invitation_token = create_user(
            FIRST_NAME, LAST_NAME, EMAIL, False)["invitation_token"]
        signup_user(invitation_token, PASSWORD)
        res = login_user(EMAIL, PASSWORD)
        self.assertEqual(res["first_name"], FIRST_NAME)
        self.assertEqual(res["first_name"], FIRST_NAME)
        self.assertIsNotNone(res.get("token"))

    def test_invite(self):
        invitation_token = create_user(
            FIRST_NAME, LAST_NAME, EMAIL, False)["invitation_token"]
        signup_user(invitation_token, PASSWORD)
        token = login_user(EMAIL, PASSWORD)["token"]
        res = post("/admin/administrators", dict(first_name="Test",
                                                 last_name="Testy", email="test@test@.io"), token)
        self.assertEqual(res.status_code, 200)

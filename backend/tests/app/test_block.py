from magellan.services.database import session_scope
from tests.app import TwoUserTestCase
from tests.requests import put, get, post
from magellan.models import UserBlock


class ProfileTests(TwoUserTestCase):

    def test_block(self):
        res = post("/app/profiles/2/block", token=self.token)
        self.assertEqual(res.status_code, 200)
        with session_scope() as session:
            x = session.query(UserBlock).first()
            self.assertIsNotNone(x)
            self.assertEqual(x.blocker_user_id, 1)
            self.assertEqual(x.user_id, 2)

    def test_block_then_query(self):
        post("/app/profiles/2/block", token=self.token)
        res = get("/app/profiles/1", token=self.token_2)
        self.assertEqual(res.status_code, 403)
        error_code = res.get_json()["error_code"]
        self.assertEqual(error_code, "BLOCKED")

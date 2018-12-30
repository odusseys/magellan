from magellan.services.database import session_scope
from tests.app import AppAuthTestCase, TwoUserTestCase, NAME_2, GENDER_ID_2
from tests.requests import put, get, post


NAME = "test2"
STATUS = "hello"
INTERESTS = [1]
AGE = 25
GENDER_ID = 2


class ProfileTests(AppAuthTestCase):

    def test_interests(self):
        res = get("/app/interests", token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 2)

    def test_update_profile(self):
        data = dict(name=NAME, status=STATUS,
                    interests=INTERESTS, age=AGE, gender_id=GENDER_ID, filters=dict(gender_filter=[1]))
        res = put("/app/profiles", data=data, token=self.token)
        self.assertEqual(res.status_code, 200)
        res = res.get_json()
        self.assertListEqual(res.get("interests"), [1])
        self.assertEqual(res.get("name"), NAME)
        self.assertEqual(res.get("status"), STATUS),
        self.assertEqual(res.get("age"), AGE)
        self.assertEqual(res.get("gender_id"), GENDER_ID)

    def test_get_after_update(self):
        data = dict(name=NAME, status=STATUS,
                    interests=INTERESTS, age=AGE, gender_id=GENDER_ID, filters=dict(gender_filter=[1]))
        res = put("/app/profiles", data=data, token=self.token).get_json()
        res2 = get("/app/profiles", token=self.token).get_json()
        self.assertDictEqual(res, res2)


class OtherProfileTests(TwoUserTestCase):

    def test_get_other_profile(self):
        res = get("/app/profiles/2", token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("name"), NAME_2)
        self.assertEqual(data.get("gender_id"), GENDER_ID_2)

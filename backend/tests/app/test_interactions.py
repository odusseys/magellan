from magellan.services.database import write, read
from magellan.models import UserFilter, Place, PlaceCategory
from tests.app import TwoUserTestCase, GENDER_ID, GENDER_ID_2, AGE, AGE_2
from tests.requests import put, get, post, delete

LOCATION = dict(lat=0.0, lng=0.0)
LOCATION2 = dict(lat=0.001, lng=0.001)
DISTANCE = 157.25


class InteractionTestCase(TwoUserTestCase):

    def start(self, user_id, activity_id):
        return post("/app/activity",
                    data=dict(
                        activity_id=activity_id,
                        location=LOCATION if user_id == 1 else LOCATION2
                    ),
                    token=self.token if user_id == 1 else self.token_2)


class GeolocationTests(InteractionTestCase):

    def test_alone(self):
        self.start(1, 1)
        res = get("/app/activity/users", params=dict(
            lat=LOCATION["lat"], lng=LOCATION["lng"], radius=200, activity_id=1), token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data)

    def test_different_activity(self):
        self.start(1, 1)
        self.start(2, 2)
        res = get("/app/activity/users", params=dict(
            lat=LOCATION["lat"], lng=LOCATION["lng"], radius=200, activity_id=1), token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data)

    def test_same_activity(self):
        self.start(1, 1)
        self.start(2, 1)
        res = get("/app/activity/users", params=dict(
            lat=LOCATION["lat"], lng=LOCATION["lng"], radius=200, activity_id=1), token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 1)
        status = data[0]
        self.assertDictContainsSubset(dict(
            user_id=2,
            location=dict(lat=LOCATION2["lat"], lng=LOCATION2["lng"]),
            active=True
        ), status)
        self.assertGreater(status.get("time_left_s"), 2300)
        self.assertIsNotNone(status.get("timer_start"))
        self.assertIsNotNone(status.get("profile_thumbnail_url"))

    def test_too_far(self):
        self.start(1, 1)
        self.start(2, 1)
        res = get("/app/activity/users", params=dict(
            lat=LOCATION["lat"], lng=LOCATION["lng"], radius=100, activity_id=1), token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data)


class SearchFilterTests(InteractionTestCase):

    def start_both(self):
        self.start(1, 1)
        self.start(2, 1)

    def put_filter(self, filter: UserFilter):
        with write() as session:
            old = session.query(UserFilter).filter(
                UserFilter.user_id == filter.user_id).first()
            if old is not None:
                session.delete(old)
                session.flush()
            session.add(filter)

    def get_search_results(self):
        res = get("/app/activity/users", params=dict(
            lat=LOCATION["lat"], lng=LOCATION["lng"], radius=200, activity_id=1), token=self.token)
        return res.get_json()

    def test_incorrect_self_gender_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id, gender_filter=[GENDER_ID]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 0)

    def correct_self_gender_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id, gender_filter=[GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 1)

    def test_correct_other_gender_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id_2, gender_filter=[GENDER_ID]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 1)

    def test_incorrect_other_gender_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id_2, gender_filter=[GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 0)

    def test_correct_self_max_age_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id, max_age=AGE_2,
            gender_filter=[GENDER_ID, GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 1)

    def test_incorrect_self_max_age_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id, max_age=AGE_2 - 1,
            gender_filter=[GENDER_ID, GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 0)

    def test_correct_self_min_age_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id, min_age=AGE_2,
            gender_filter=[GENDER_ID, GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 1)

    def test_incorrect_self_min_age_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id, min_age=AGE_2 + 1,
            gender_filter=[GENDER_ID, GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 0)

    def test_correct_other_max_age_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id_2, max_age=AGE,
            gender_filter=[GENDER_ID, GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 1)

    def test_incorrect_other_max_age_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id_2, max_age=AGE - 1,
            gender_filter=[GENDER_ID, GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 0)

    def test_correct_other_min_age_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id_2, min_age=AGE,
            gender_filter=[GENDER_ID, GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 1)

    def test_incorrect_other_min_age_filter(self):
        self.put_filter(UserFilter(
            user_id=self.user_id_2, min_age=AGE + 1,
            gender_filter=[GENDER_ID, GENDER_ID_2]))
        self.start_both()
        res = self.get_search_results()
        self.assertEqual(len(res), 0)


class TestPlaceInterests(InteractionTestCase):

    def test_place_interests(self):
        with write() as session:
            session.add(PlaceCategory(name="test"))
            session.flush()
            session.add(
                Place(name="test", google_place_id="test", place_category_id=1))
        self.start(1, 1)
        self.start(2, 1)

        # notify interest
        res = post("/app/activity/places/1/interests", dict(), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        # self should not return results
        res = get("/app/activity/places/1/interests", dict(), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["results"]), 0)

        # for other should return 1 result
        res = get("/app/activity/places/1/interests", dict(), self.token_2)
        self.assertEqual(res.status_code, 200)
        results = res.get_json()["results"]
        self.assertEqual(len(results), 1)

        # results should be the user status
        status = get("/app/activity/users/1", dict(), self.token_2).get_json()
        self.assertDictEqual(results[0], status)

        # remove interest
        res = delete("/app/activity/places/1/interests", dict(), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        # should no longer appear for other
        res = get("/app/activity/places/1/interests", dict(), self.token_2)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["results"]), 0)

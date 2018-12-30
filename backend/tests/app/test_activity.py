from magellan.services.database import write
from magellan.models import Place, PlaceCategory, PlaceActivity
from magellan.util.geometry import make_point
from tests.app import AppAuthTestCase
from tests.requests import put, get, post, delete

LOCATION = dict(lat=0.0, lng=0.0)
LOCATION2 = dict(lat=0.001, lng=0.001)
DISTANCE = 157.25


class ActivityTests(AppAuthTestCase):

    def start(self, activity_id=1):
        return post("/app/activity",
                    data=dict(
                        activity_id=activity_id,
                        location=LOCATION
                    ),
                    token=self.token)

    def test_activity_list(self):
        res = get("/app/activities", token=self.token)
        self.assertEqual(res.status_code, 200)
        self.assertListEqual(res.get_json(), [dict(
            id=1,
            name="test",
            icon_url="https://static.magellan-app.io/activities/test.svg"
        ), dict(
            id=2,
            name="test2",
            icon_url="https://static.magellan-app.io/activities/test2.svg"
        )])

    def test_start_and_get(self):
        res = self.start()
        self.assertEqual(res.status_code, 200)
        res = get("/app/activity", token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("active"))
        self.assertEqual(data.get("activity_id"), 1)
        self.assertDictEqual(data.get("location"), LOCATION)

    def test_inactive(self):
        res = get("/app/activity", token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data.get("active"))

    def test_update_location(self):
        self.start()
        res = put("/app/activity/location",
                  data=dict(location=LOCATION2), token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertDictEqual(data.get("location"), LOCATION2)
        data = get("/app/activity", token=self.token).get_json()
        self.assertDictEqual(data.get("location"), LOCATION2)

    def test_stop_and_resume_localization(self):
        self.start()
        res = delete("/app/activity/location", token=self.token)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.get_json().get("active"))
        res = get("/app/activity", token=self.token)
        self.assertFalse(res.get_json().get("active"))

        res = put("/app/activity/location",
                  data=dict(location=LOCATION2), token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("active"))
        self.assertDictEqual(data.get("location"), LOCATION2)
        data = get("/app/activity", token=self.token).get_json()
        self.assertTrue(data.get("active"))
        self.assertDictEqual(data.get("location"), LOCATION2)

    def test_places_nearby(self):
        with write() as session:
            session.add(PlaceCategory(name="test"))
            session.flush()
            session.add(Place(
                name="test",
                place_category_id=1,
                google_place_id="test",
                coordinates=make_point(
                    LOCATION2["lat"], LOCATION2["lng"])))
            session.flush()
            session.add(PlaceActivity(place_id=1, activity_id=1))
        self.start()

        # should return the place
        res = get("/app/activity/places",
                  dict(lat=LOCATION["lat"], lng=LOCATION["lng"], radius=200), self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["results"]
        self.assertEqual(len(data), 1)
        data = data[0]
        self.assertEqual(data["name"], "test")
        self.assertEqual(data["id"], 1)

        # too far
        res = get("/app/activity/places",
                  dict(lat=LOCATION["lat"], lng=LOCATION["lng"], radius=100), self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["results"]
        self.assertEqual(len(data), 0)

    def test_wrong_activity(self):
        with write() as session:
            session.add(PlaceCategory(name="test"))
            session.flush()
            session.add(Place(
                name="test",
                place_category_id=1,
                google_place_id="test",
                coordinates=make_point(
                    LOCATION2["lat"], LOCATION2["lng"])))
            session.flush()
            session.add(PlaceActivity(place_id=1, activity_id=1))
        self.start(2)

        res = get("/app/activity/places",
                  dict(lat=LOCATION["lat"], lng=LOCATION["lng"], radius=200), self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["results"]
        self.assertEqual(len(data), 0)

from tests.app import TwoUserTestCase
from tests.requests import post, get, put
from tests.mock.notifications import get_notifications
from magellan.services.database import write, read
from magellan.models import Place, PlaceCategory, MeetupUserRating, MeetupNoShow
from magellan.util.geometry import make_point

LOCATION = dict(lat=0.0, lng=0.0)
LOCATION2 = dict(lat=0.003, lng=0.003)
PLACE_LOCATION = dict(lat=0.001, lng=0.001)


class MeetupTests(TwoUserTestCase):
    """
        All tests follow the same starting pattern: user 1 and 2 have a thread and user 2 accepts a meetup.
    """

    def start(self, from_place=False):
        with write() as session:
            session.add(PlaceCategory(name="test"))
            session.flush()
            session.add(Place(
                name="test",
                google_place_id="test",
                coordinates=make_point(
                    PLACE_LOCATION["lat"], PLACE_LOCATION["lng"]
                ),
                place_category_id=1
            ))
        post("/app/activity",
             data=dict(activity_id=1, location=LOCATION),
             token=self.token)
        post("/app/activity",
             data=dict(activity_id=1, location=LOCATION2),
             token=self.token_2)
        post("/app/chat/messages",
             dict(recipient_user_id=self.user_id_2, data=dict(text="test")),
             self.token)
        res = post("/app/meetups",
                   data=dict(thread_id=1,
                             location=None if from_place else PLACE_LOCATION,
                             place_id=1 if from_place else None),
                   token=self.token_2)
        self.assertEqual(res.status_code, 200)
        self.meetup_id = res.get_json()["id"]

    def arrive(self, user_id):
        res = put("/app/meetups/1/location",
                  dict(location=PLACE_LOCATION),
                  self.token if user_id == self.user_id else self.token_2)
        self.assertEqual(res.status_code, 200)

    def test_accept_notification(self):
        self.start()
        notifs = get_notifications(1)
        self.assertEqual(len(notifs), 1)
        notif = notifs[0]["data"]
        self.assertEqual(notif["notification_type"], "MEETUP_ACCEPTED")
        self.assertEqual(notif["payload"]["id"], 1)

    def test_accept_and_get(self):
        self.start()
        res = get("/app/meetups", token=self.token_2)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["results"]
        self.assertEqual(len(data), 1)

        res = get("/app/meetups", token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["results"]
        self.assertEqual(len(data), 1)
        meetup_data = data[0]
        self.assertEqual(meetup_data["partner_user_id"], 2)

        res = get("/app/meetups/1", token=self.token)
        self.assertEqual(res.status_code, 200)
        self.assertDictEqual(meetup_data, res.get_json())

        res = get("/app/meetups/1/status", token=self.token)
        data = res.get_json()
        self.assertFalse(data["cancelled"])
        self.assertFalse(data["concluded"])
        self.assertFalse(data["arrived"])
        self.assertDictEqual(data["location"], LOCATION)

        res = get("/app/meetups/1/partner/status", token=self.token)
        data = res.get_json()
        self.assertFalse(data["cancelled"])
        self.assertFalse(data["concluded"])
        self.assertFalse(data["arrived"])
        self.assertDictEqual(data["location"], LOCATION2)

    def test_cancel(self):
        self.start()
        res = post("/app/meetups/1/cancel", token=self.token)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        # check user was notified
        notifications = get_notifications(2)
        self.assertEqual(len(notifications), 2)  # first is message
        data = notifications[1]["data"]
        self.assertEqual(data["notification_type"], "MEETUP_CANCEL")
        self.assertEqual(data["payload"]["meetup_id"], 1)

        # check meetup is over
        res = get("/app/meetups/1", token=self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["cancelled"])
        self.assertTrue(data["concluded"])

    def test_arrive(self):
        self.start()
        # first test updating location to same location does not trigger arrival
        res = put("/app/meetups/1/location",
                  dict(location=LOCATION), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        res = get("/app/meetups/1/status", token=self.token)
        data = res.get_json()
        self.assertFalse(data["arrived"])

        self.arrive(1)

        res = get("/app/meetups/1/status", token=self.token)
        data = res.get_json()
        self.assertTrue(data["arrived"])
        self.assertDictEqual(data["location"], PLACE_LOCATION)

        res = get("/app/meetups/1/partner/status", token=self.token_2)
        data = res.get_json()
        self.assertTrue(data["arrived"])
        self.assertDictEqual(data["location"], PLACE_LOCATION)

        # check notifications
        notifs_1 = get_notifications(1)
        self.assertEqual(len(notifs_1), 2)
        notif_1 = notifs_1[1]["data"]
        self.assertEqual(notif_1["notification_type"], "SELF_IS_CLOSE")
        self.assertEqual(notif_1["payload"]["meetup_id"], 1)

        notifs_2 = get_notifications(2)
        self.assertEqual(len(notifs_2), 2)
        notif_2 = notifs_2[1]["data"]
        self.assertEqual(notif_2["notification_type"], "PARTNER_IS_CLOSE")
        self.assertEqual(notif_2["payload"]["meetup_id"], 1)

    def test_arrive_for_place(self):
        self.start(True)
        self.arrive(1)

        res = get("/app/meetups/1/status", token=self.token)
        data = res.get_json()
        self.assertTrue(data["arrived"])
        self.assertDictEqual(data["location"], PLACE_LOCATION)

    def test_rate(self):
        self.start()

        # try rating without arriving
        res = post("/app/meetups/1/partner/rating",
                   dict(rating_id=1), self.token)
        self.assertEqual(res.status_code, 400)

        self.arrive(1)
        res = post("/app/meetups/1/partner/rating",
                   dict(rating_id=1), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        res = get("/app/meetups/1", token=self.token)
        self.assertTrue(res.get_json()["concluded"])
        res = get("/app/meetups/1", token=self.token_2)
        self.assertFalse(res.get_json()["concluded"])

        with read() as session:
            rating = session.query(MeetupUserRating).first()
            self.assertIsNotNone(rating)
            self.assertEqual(rating.user_id, self.user_id_2)
            self.assertEqual(rating.rating_id, 1)
            self.assertEqual(rating.meetup_id, 1)

    def test_noshow(self):
        self.start()

        # try noshow without arriving
        res = post("/app/meetups/1/partner/noshow",
                   dict(rating_id=1), self.token)
        self.assertEqual(res.status_code, 400)

        self.arrive(1)
        res = post("/app/meetups/1/partner/noshow",
                   dict(rating_id=1), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        res = get("/app/meetups/1", token=self.token)
        self.assertTrue(res.get_json()["concluded"])
        res = get("/app/meetups/1", token=self.token_2)
        self.assertTrue(res.get_json()["concluded"])

        with read() as session:
            rating = session.query(MeetupNoShow).first()
            self.assertIsNotNone(rating)
            self.assertEqual(rating.user_id, self.user_id_2)
            self.assertEqual(rating.meetup_id, 1)

    def test_skip(self):
        self.start()

        # try noshow without arriving
        res = post("/app/meetups/1/partner/skip",
                   dict(rating_id=1), self.token)
        self.assertEqual(res.status_code, 400)

        self.arrive(1)
        res = post("/app/meetups/1/partner/skip",
                   dict(rating_id=1), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        res = get("/app/meetups/1", token=self.token)
        self.assertTrue(res.get_json()["concluded"])
        res = get("/app/meetups/1", token=self.token_2)
        self.assertFalse(res.get_json()["concluded"])

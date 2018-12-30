from magellan.services.database import read, write
from magellan.models import Thread, Message, Place, PlaceCategory
from tests.app import TwoUserTestCase
from tests.requests import put, get, post, delete
from tests.mock.notifications import get_notifications


class ChatTests(TwoUserTestCase):

    def test_send_text(self):
        res = post("/app/chat/messages",
                   dict(recipient_user_id=self.user_id_2, data=dict(text="test")), self.token)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertDictEqual(data, dict(
            thread_id=1, text="test", id=1, location=None, place_id=None, sender_user_id=1))

        # check created in db
        with read() as session:
            thread = session.query(Thread).all()
            self.assertEqual(len(thread), 1)
            thread = thread[0]
            self.assertEqual(thread.creator_user_id, self.user_id)
            self.assertEqual(thread.recipient_user_id, self.user_id_2)
            messages = session.query(Message).all()
            self.assertEqual(len(messages), 1)
            message = messages[0]
            self.assertEqual(message.text, "test")
            self.assertEqual(message.sender_user_id, self.user_id)
            self.assertIsNone(message.coordinates)
            self.assertIsNone(message.place_id)

        # check other user's notifications
        notifs = get_notifications(self.user_id_2)
        self.assertEqual(len(notifs), 1)
        notif_data = notifs[0]["data"]["payload"]
        self.assertDictEqual(data, notif_data)

        res = get('/app/chat/messages', dict(thread_id=1), self.token_2)
        self.assertEqual(res.get_json().get("messages")[0], data)

    def test_send_place(self):
        with write() as session:
            session.add(PlaceCategory(name="test"))
            session.flush()
            session.add(
                Place(name="test", google_place_id="test", place_category_id=1))
        res = post("/app/chat/messages",
                   dict(recipient_user_id=self.user_id_2, data=dict(place_id=1)), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["place_id"], 1)

    def test_send_location(self):
        res = post("/app/chat/messages",
                   dict(recipient_user_id=self.user_id_2, data=dict(location=dict(lng=0, lat=0))), self.token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["location"], dict(lat=0.0, lng=0.0))

    def test_pagination(self):
        for i in range(25):
            post("/app/chat/messages",
                 dict(recipient_user_id=self.user_id_2, data=dict(text="test_{}".format(i))), self.token)

        res = get('/app/chat/messages', dict(thread_id=1), self.token_2)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        messages = data.get("messages")
        cursor = data.get("cursor")
        self.assertEqual(len(messages), 20)
        self.assertIsNotNone(cursor)

        res = get("/app/chat/messages",
                  dict(thread_id=1, cursor=cursor), self.token_2)
        data = res.get_json()
        messages_2 = data.get("messages")
        cursor = data.get("cursor")
        self.assertEqual(len(messages_2), 5)
        self.assertIsNotNone(cursor)
        messages.extend(messages_2)
        texts = set(x["text"] for x in messages)
        self.assertSetEqual(texts, set("test_{}".format(i) for i in range(25)))

        res = get("/app/chat/messages",
                  dict(thread_id=1, cursor=cursor), self.token_2)
        data = res.get_json()
        self.assertFalse(data.get("messages"))
        self.assertEqual(cursor, data.get("cursor"))

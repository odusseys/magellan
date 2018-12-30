import magellan.services.sms as sms

MAILBOX = {}


def delete_all():
    MAILBOX.clear()


def get_messages(phone_number):
    return MAILBOX.get(phone_number, [])


def send_sms(phone_number, content):
    if phone_number not in MAILBOX:
        MAILBOX[phone_number] = []
    MAILBOX[phone_number].append(content)


# do the monkey patch hee hee
sms.sns = None  # in case
sms.send_text = send_sms

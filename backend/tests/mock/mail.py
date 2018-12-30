import magellan.services.mail as mail

MAILBOX = {}


def delete_all():
    MAILBOX.clear()


def get_messages(email):
    return MAILBOX.get(email, [])


def send_email(to_addresses, subject, content):
    for to in to_addresses:
        if to not in MAILBOX:
            MAILBOX[to] = []
        MAILBOX[to].append(dict(subject=subject, content=content))


# do the monkey patch hee hee
mail.client = None
mail.send_mail = send_email

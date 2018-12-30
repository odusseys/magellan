import boto3

client = boto3.client("ses")

SENDER = "noreply@magellan-app.io"


def send_mail(to: [str], subject: str, content: str):
    client.send_email(
        Source=SENDER,
        Destination=dict(ToAddresses=to),
        Message=dict(
            Subject=dict(Data=subject),
            Body=dict(Text=dict(Data=content))
        )
    )

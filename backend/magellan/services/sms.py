import boto3

sns = boto3.client('sns')


def send_text(phone_number: str, content: str):
    sns.publish(PhoneNumber=phone_number, Message=content)

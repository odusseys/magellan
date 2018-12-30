import boto3

client = boto3.client("s3")


def upload_file(bucket, key, data):
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data
    )


def get_file(bucket, key):
    res = client.get_object(
        Bucket=bucket,
        Key=key
    )
    return res["Body"].read()


def delete_file(bucket, key):
    client.delete_object(
        Bucket=bucket,
        Key=key
    )


def generate_presigned_url(bucket, key):
    return client.generate_presigned_url(ClientMethod="get_object", Params=dict(
        Bucket=bucket,
        Key=key
    ))

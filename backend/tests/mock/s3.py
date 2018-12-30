import magellan.services.s3 as s3

S3 = dict()


def generate_presigned_url(bucket, key):
    return "test"


def upload_file(bucket, key, data):
    S3[bucket + key] = data


def delete_file(bucket, key):
    del S3[bucket + key]


def delete_all():
    S3.clear()


def get_file(bucket, key):
    return S3[bucket + key]


s3.client = None
s3.generate_presigned_url = generate_presigned_url
s3.upload_file = upload_file

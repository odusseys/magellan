from tests import app
import json

client = app.test_client()


def get(endpoint, params=None, token=None):
    headers = dict() if token is None else dict(Authorization=f"Bearer {token}")
    return client.get(endpoint, data=params or dict(), headers=headers)


def delete(endpoint, params=None, token=None):
    headers = dict() if token is None else dict(Authorization=f"Bearer {token}")
    return client.delete(endpoint, data=params or dict(), headers=headers)


def post(endpoint, data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    data = json.dumps(data or dict())
    return client.post(endpoint, data=data, headers=headers)


def put(endpoint, data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    data = json.dumps(data or dict())
    return client.put(endpoint, data=data, headers=headers)

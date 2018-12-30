import os
import pkg_resources


def _load_env_file():
    try:
        env = pkg_resources.resource_string(__name__, '.env').decode('utf-8')
        for line in env.split("\n"):
            if not line:
                continue
            [x, y] = line.split("=")
            print("Loading environment: {}={}".format(x, y))
            if x not in os.environ:
                os.environ[x] = y
    except FileNotFoundError:
        return


_load_env_file()


def _get_required_env(name):
    res = os.environ.get(name)
    if res is None:
        raise ValueError("Missing in environment: {}".format(name))
    return res


REDIS_HOST = os.environ.get("REDIS_HOST")
DATABASE_URL = _get_required_env("DATABASE_URL")
APP_JWT_SECRET = _get_required_env("APP_JWT_SECRET")
AWS_ACCESS_KEY_ID = _get_required_env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = _get_required_env("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = _get_required_env("AWS_DEFAULT_REGION")

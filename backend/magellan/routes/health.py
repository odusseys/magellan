from magellan.routes import magellan
from magellan.services.database import session_scope
import magellan.services.redis as redis
from magellan.models import AdminUser


@magellan.route("/health", methods=["GET"])
def test():
    # test connection to DB
    with session_scope() as session:
        session.query(AdminUser).first()
    redis.test_connection()
    return "healthy", 200


@magellan.route("/error", methods=["GET"])
def error():
    raise ValueError("Just testing")

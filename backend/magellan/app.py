from flask import Flask
from flask_cors import CORS
from magellan.routes import magellan
from magellan.services.database import db
from magellan.env import DATABASE_URL


def get_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(magellan)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    db.app = app  # dirty hack so we can use it in shell
    return app

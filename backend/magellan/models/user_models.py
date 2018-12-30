from magellan.services.database import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    age = db.Column(db.Integer)
    gender_id = db.Column(db.Integer, db.ForeignKey(Gender.id))
    status = db.Column(db.String(250), nullable=False, default="")


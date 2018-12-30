from magellan.services.database import db


class User(db.Model):
    __tablename__ = 'admin_user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(250), unique=True)


class Account(db.Model):
    __tablename__ = 'admin_user_account'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(AdminUser.id, ondelete="cascade"), index=True)
    hashed_password = db.Column(db.String(250), nullable=False)

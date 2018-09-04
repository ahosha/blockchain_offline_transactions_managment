# The examples in this file come from the Flask-SQLAlchemy documentation
# For more information take a look at:
# http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#simple-relationships

from datetime import datetime

from src.database import db
from sqlalchemy.sql import func


class Withdraw(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ext_account_id = db.Column(db.String(256))
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, ext_account_id):
        self.ext_account_id = ext_account_id

    def __repr__(self):
        return '<Account: %r>' % self.ext_account_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
